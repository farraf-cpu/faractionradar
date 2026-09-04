"""Fetch Kalshi Economics-category market data and POST to calendar-worker
/upload-markets. Runs from GHA so the request hits Kalshi from a residential
IP pool, bypassing the persistent 429 our Cloudflare edge worker gets from
api.elections.kalshi.com.

For each marquee slug (nfp/cpi/fomc), pull the series' events + their full
market ladders + orderbook top-of-book yes-prices. Ship the raw snapshot to
the worker so the worker can compute implied central estimates without ever
having to fetch Kalshi itself.

Env (set by workflow):
  UPLOAD_AUTH_KEY       — matches worker's UPLOAD_AUTH_KEY secret
  CALENDAR_WORKER_URL   — https://faractionradar-calendar.faractionradar.workers.dev

Exit codes:
  0 = at least one series pulled + POSTed successfully
  1 = all series failed
  2 = missing required env
  3 = POST rejected by worker
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone

KALSHI_BASE = "https://api.elections.kalshi.com/trade-api/v2"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

# Series tickers per marquee type. Verified 2026-09-02 via the worker's
# ?kalshi-diag endpoint against Kalshi's /series?category=Economics list.
KALSHI_SERIES = {
    "nfp":  ["KXUSNFP", "KXPAYROLLS"],
    "cpi":  ["KXCPI", "KXECONSTATCPI"],
    "fomc": ["KXFEDDECISION", "KXFED"],
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[fetch-kalshi] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def get_json(url: str, timeout: int = 20) -> dict | list | None:
    req = urllib.request.Request(url, headers={
        "user-agent": UA,
        "accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"[fetch-kalshi] HTTP {e.code} on {url}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[fetch-kalshi] {type(e).__name__} on {url}: {e}", file=sys.stderr)
        return None


def _num(v):
    """Kalshi returns prices as string decimals in newer API ('0.9600'), older
    endpoints used integer cents. Handle both."""
    if v is None:
        return None
    if isinstance(v, str):
        try:
            return float(v)
        except ValueError:
            return None
    if isinstance(v, (int, float)):
        # Heuristic: if >= 1 it's cents (Kalshi old API), scale down
        return v / 100.0 if v > 1 else float(v)
    return None


def fetch_market_detail(ticker: str) -> dict | None:
    """Individual market fetch — this is the endpoint that carries live prices.
    Bulk /markets?event_ticker=X returns definitions only (all prices null).
    Kalshi's newer API uses `*_dollars` string fields; older uses integer
    cents on `yes_bid`/`yes_ask`. This handles both."""
    url = f"{KALSHI_BASE}/markets/{urllib.parse.quote(ticker)}"
    data = get_json(url)
    if not data or not isinstance(data, dict):
        return None
    m = data.get("market") or {}

    # Prefer new *_dollars string fields; fall back to legacy names.
    yes_bid = _num(m.get("yes_bid_dollars") or m.get("yes_bid"))
    yes_ask = _num(m.get("yes_ask_dollars") or m.get("yes_ask"))
    last = _num(m.get("last_price_dollars") or m.get("last_price"))
    # If yes-side prices are missing, derive from no-side: yes = 1 - no.
    if yes_bid is None:
        na = _num(m.get("no_ask_dollars") or m.get("no_ask"))
        if na is not None:
            yes_bid = round(1.0 - na, 4)
    if yes_ask is None:
        nb = _num(m.get("no_bid_dollars") or m.get("no_bid"))
        if nb is not None:
            yes_ask = round(1.0 - nb, 4)

    return {
        "ticker": m.get("ticker"),
        "title": m.get("title"),
        "subtitle": m.get("subtitle") or m.get("yes_sub_title") or m.get("no_sub_title"),
        "status": m.get("status"),
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "last_price": last,
        "volume": _num(m.get("volume_dollars") or m.get("volume")),
        "open_interest": _num(m.get("open_interest_fp") or m.get("open_interest")),
        "close_time": m.get("close_time"),
        "expiration_time": m.get("expiration_time"),
    }


def fetch_event_markets_with_prices(event_ticker: str, market_tickers: list[str]) -> list[dict]:
    """For each market ticker under an event, fetch full detail (with prices)."""
    out = []
    for t in market_tickers:
        m = fetch_market_detail(t)
        if m:
            out.append(m)
        time.sleep(0.1)  # pacing between per-market fetches
    return out


def fetch_series_snapshot(series_ticker: str) -> dict | None:
    """Pull the series' events (with nested market list) + fetch per-market
    prices for the SINGLE next-upcoming event. Older/further events kept as
    structure-only (no prices) so we can still show them in listings without
    hammering Kalshi with hundreds of per-market fetches."""
    events_url = (
        f"{KALSHI_BASE}/events?series_ticker={urllib.parse.quote(series_ticker)}"
        "&limit=100&with_nested_markets=true"
    )
    events_data = get_json(events_url)
    if not events_data or not isinstance(events_data, dict):
        return None
    events = events_data.get("events") or []

    # Pick the nearest-future event as our "focus". Kalshi events often
    # show close_time: null even for real active events — fall back to the
    # earliest close_time across the event's nested markets (which IS
    # populated). Filter out events whose derived close_time is in the past.
    today_iso = datetime.now(timezone.utc).date().isoformat()
    def derived_close(ev):
        if ev.get("close_time"):
            return ev["close_time"]
        market_closes = [m.get("close_time") for m in (ev.get("markets") or []) if m.get("close_time")]
        return min(market_closes) if market_closes else None
    # Debug: log ALL events + their derived_close so we can diagnose why
    # focus is picking a resolved-cycle event (2026-09 investigation).
    print(f"::group::{series_ticker} events ({len(events)} total)")
    for ev in events[:15]:
        ec = ev.get("close_time")
        dc = derived_close(ev)
        first_mkt_close = None
        first_mkt_status = None
        if ev.get("markets"):
            first_mkt_close = ev["markets"][0].get("close_time")
            first_mkt_status = ev["markets"][0].get("status")
        print(f"  {ev.get('event_ticker')} | status={ev.get('status')} | close_time={ec} | derived={dc} | first_mkt_close={first_mkt_close} first_mkt_status={first_mkt_status}")
    print("::endgroup::")
    with_close = []
    for ev in events:
        c = derived_close(ev)
        if not c:
            continue  # can't date it; skip
        if c[:10] < today_iso:
            continue  # past
        with_close.append((c, ev))
    with_close.sort(key=lambda x: x[0])
    focus_event = with_close[0][1] if with_close else None
    if focus_event:
        print(f"[fetch_kalshi] {series_ticker} focus: {focus_event.get('event_ticker')} (close={derived_close(focus_event)})")
    else:
        print(f"[fetch_kalshi] {series_ticker} NO future events found — all {len(events)} events filtered out")

    enriched = []
    for ev in events:
        markets_stub = ev.get("markets") or []
        market_tickers = [m.get("ticker") for m in markets_stub if m.get("ticker")]
        if focus_event and ev.get("event_ticker") == focus_event.get("event_ticker"):
            # Focus event: pull per-market detail with real prices.
            markets = fetch_event_markets_with_prices(ev.get("event_ticker"), market_tickers)
        else:
            # Other events: keep structure only, no prices. Save on API calls.
            markets = [{
                "ticker": m.get("ticker"),
                "title": m.get("title"),
                "subtitle": m.get("subtitle") or m.get("yes_sub_title"),
                "status": m.get("status"),
                "yes_bid": None, "yes_ask": None, "last_price": None,
                "volume": None, "open_interest": None,
                "close_time": m.get("close_time"),
                "expiration_time": m.get("expiration_time"),
            } for m in markets_stub]
        enriched.append({
            "event_ticker": ev.get("event_ticker"),
            "title": ev.get("title"),
            "close_time": ev.get("close_time"),
            "status": ev.get("status"),
            "is_focus": focus_event is not None and ev.get("event_ticker") == focus_event.get("event_ticker"),
            "markets": markets,
        })
    return {
        "series_ticker": series_ticker,
        "events": enriched,
        "focus_event_ticker": focus_event.get("event_ticker") if focus_event else None,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    upload_key = require_env("UPLOAD_AUTH_KEY")
    worker_url = require_env("CALENDAR_WORKER_URL").rstrip("/") + "/upload-markets"

    payload_by_type: dict[str, list[dict]] = {}
    total_events = 0
    for slug_type, series_list in KALSHI_SERIES.items():
        snapshots = []
        for st in series_list:
            snap = fetch_series_snapshot(st)
            if snap is None:
                print(f"[fetch-kalshi] {slug_type} :: {st} => fetch failed")
                continue
            snapshots.append(snap)
            total_events += len(snap.get("events") or [])
            print(f"[fetch-kalshi] {slug_type} :: {st} => {len(snap.get('events') or [])} events, "
                  f"{sum(len(e.get('markets') or []) for e in snap.get('events') or [])} markets")
        if snapshots:
            payload_by_type[slug_type] = snapshots

    if not payload_by_type:
        print("[fetch-kalshi] all series failed — nothing to upload", file=sys.stderr)
        return 1

    payload = {
        "kalshi": payload_by_type,
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "totalEvents": total_events,
    }
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        worker_url,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": upload_key,
            "user-agent": UA,  # CF-1010 defense (see phase-1 learnings rule 1)
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[fetch-kalshi] worker → {res.status} {res.reason}")
            print(f"[fetch-kalshi] response: {res.read().decode('utf-8')[:400]}")
            return 0
    except urllib.error.HTTPError as e:
        print(f"[fetch-kalshi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
