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


def fetch_markets_for_event(event_ticker: str) -> list[dict]:
    """One call returns every market under an event with its current prices.
    Way more efficient than per-market orderbook fetches AND avoids the
    burst-rate-limit that killed the previous approach."""
    url = f"{KALSHI_BASE}/markets?event_ticker={urllib.parse.quote(event_ticker)}&limit=200"
    data = get_json(url)
    if not data or not isinstance(data, dict):
        return []
    out = []
    for m in data.get("markets") or []:
        # Kalshi returns prices in cents (0-100). Convert to probability.
        def cents(v):
            return v / 100.0 if isinstance(v, (int, float)) else None
        out.append({
            "ticker": m.get("ticker"),
            "title": m.get("title"),
            "subtitle": m.get("subtitle") or m.get("yes_sub_title"),
            "status": m.get("status"),
            "yes_bid": cents(m.get("yes_bid")),
            "yes_ask": cents(m.get("yes_ask")),
            "last_price": cents(m.get("last_price")),
            "volume": m.get("volume"),
            "open_interest": m.get("open_interest"),
            "close_time": m.get("close_time"),
            "expiration_time": m.get("expiration_time"),
        })
    return out


def fetch_series_snapshot(series_ticker: str) -> dict | None:
    """Pull the series' events + a per-event /markets call to get full prices."""
    events_url = (
        f"{KALSHI_BASE}/events?series_ticker={urllib.parse.quote(series_ticker)}&limit=100"
    )
    events_data = get_json(events_url)
    if not events_data or not isinstance(events_data, dict):
        return None
    events = events_data.get("events") or []
    enriched = []
    for ev in events:
        et = ev.get("event_ticker")
        markets = fetch_markets_for_event(et) if et else []
        time.sleep(0.15)  # gentle pacing to avoid a burst 429
        enriched.append({
            "event_ticker": et,
            "title": ev.get("title"),
            "close_time": ev.get("close_time"),
            "status": ev.get("status"),
            "markets": markets,
        })
    return {
        "series_ticker": series_ticker,
        "events": enriched,
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
