"""FOMC predictor + emitter. v1-simple-blend: publishes an implied
federal funds target rate as a point estimate (not a discrete outcome
distribution — that's Phase 2). Prediction markets dominate the blend
because they've historically led rate-decision calls.

Env (set by GHA workflow):
  UPLOAD_AUTH_KEY       — POST auth to /upload
  CALENDAR_WORKER_URL   — https://faractionradar-calendar.faractionradar.workers.dev
  FOMC_RELEASE_DATE     — YYYY-MM-DD
  FOMC_DAYS_OUT         — 7|4|3|2|1
  FOMC_MARKET_RATE      — Kalshi-implied rate (parsed by workflow from /public/kalshi-implied fomc.value_k)
  FRED_API_KEY          — optional; used for current fed funds target fallback
  MODEL_VERSION         — default "v1-simple-blend"

Note: consensus for FOMC is often blank in FF (rare release with no forecast
column), so we rely on markets + current-rate anchor. Consensus is wired
optionally via FOMC_CONSENSUS_RATE for later expansion.
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

# Historical MAE benchmarks (percentage points on target rate).
# Market: Kalshi/fed-funds-futures typically ~5bp (0.05pp) on rate-decision
# days. Consensus: analysts often stop publishing FF forecasts entirely,
# but when they do, ~7bp. Anchor (current rate) is a no-change assumption
# with wide error — only used as fallback so we don't return zero.
MAE = {
    "market":    0.05,
    "consensus": 0.07,
    "anchor":    0.25,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-fomc] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_rate(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fetch_current_fed_funds(api_key: str) -> float | None:
    """DFEDTARU (upper bound of target range) — most recent observation.
    Returns rate as a percent (e.g. 4.25 for 4.25%)."""
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id=DFEDTARU&api_key={urllib.parse.quote(api_key)}"
           "&file_type=json&sort_order=desc&limit=1")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-fomc] FRED DFEDTARU fetch failed: {e}", file=sys.stderr)
        return None
    obs = data.get("observations") or []
    if not obs:
        return None
    v = obs[0].get("value")
    if v in (None, ".", ""):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def blend(market: float | None,
          consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if market is not None:
        parts.append(("market", market, MAE["market"]))
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if anchor is not None:
        parts.append(("anchor", anchor, MAE["anchor"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


def format_rate(pct: float) -> str:
    """FOMC convention: two decimals, e.g. '4.25%'."""
    return f"{pct:.2f}%"


def lean_vs_current(point: float, anchor: float | None) -> str:
    if anchor is None:
        return "no current-rate anchor available"
    delta_bp = round((point - anchor) * 100)
    if abs(delta_bp) < 5:
        return "hold expected (in line with current target)"
    if delta_bp <= -25:
        return f"cut of ~{abs(delta_bp)}bp expected"
    if delta_bp >= 25:
        return f"hike of ~{delta_bp}bp expected"
    return f"{delta_bp:+d}bp move vs current expected"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, market: float | None,
                    consensus: float | None, anchor: float | None,
                    used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else format_rate(v)} | {MAE[name]:.2f} pp |"
        for name, v in (("market", market), ("consensus", consensus), ("anchor", anchor))
    )
    return f"""# FOMC prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_rate(point)}** target fed funds rate

- 68% CI: [{point - sigma:.2f}%, {point + sigma:.2f}%]
- 95% CI: [{point - 2*sigma:.2f}%, {point + 2*sigma:.2f}%]
- Direction: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

v1-simple-blend: inverse-MAE-weighted mean of the sub-models above. Markets
carry ~10x the weight of the current-rate anchor because prediction markets
have historically led Fed rate calls. Phase 2 target is a proper discrete-
outcome model (probability distribution over hold / cut25 / cut50 / hike25)
using fed funds futures + SEP dot-plot + speaker-hawkishness index.

Point estimate is a scalar rate (e.g. "4.25%") not a discrete outcome.
That's a simplification — the true prediction is a distribution over
outcomes. Phase 2 will publish the full distribution.
"""


def append_ledger(payload: dict) -> None:
    ledger = ROOT / "predictions.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": auth_key,
            "user-agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[emit-fomc] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-fomc] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "FOMC_RELEASE_DATE", "FOMC_DAYS_OUT"):
        require_env(k)

    release = os.environ["FOMC_RELEASE_DATE"]
    days_out = int(os.environ["FOMC_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    market = parse_rate("FOMC_MARKET_RATE")
    consensus = parse_rate("FOMC_CONSENSUS_RATE")
    fred_key = os.environ.get("FRED_API_KEY")
    anchor = fetch_current_fed_funds(fred_key) if fred_key else None

    if market is None and consensus is None and anchor is None:
        print("[emit-fomc] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(market, consensus, anchor)
    lean = lean_vs_current(point, anchor)

    print(f"[emit-fomc] FOMC {release} T-{days_out}: {format_rate(point)} "
          f"(sigma {sigma:.3f}pp, used: {', '.join(used)})")
    if market    is not None: print(f"  market:     {market:.2f}%")
    if consensus is not None: print(f"  consensus:  {consensus:.2f}%")
    if anchor    is not None: print(f"  anchor:     {anchor:.2f}%")

    prediction = {
        "eventSlug": f"fomc-{release}",
        "eventTitle": "FOMC federal funds rate decision",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_rate(point),
            "lean": lean,
            "ci68": [round(point - sigma, 2), round(point + sigma, 2)],
            "ci95": [round(point - 2 * sigma, 2), round(point + 2 * sigma, 2)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/fomc-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                market, consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"fomc-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-fomc] wrote {report_path.relative_to(ROOT)}")

    ledger_row = {
        "publishedAt": prediction["ourCall"]["publishedAt"],
        "eventSlug": prediction["eventSlug"],
        "daysOut": days_out,
        "modelVersion": model_version,
        "ourCall": prediction["ourCall"]["value"],
        "ci68": prediction["ourCall"]["ci68"],
        "grandMedian": None,
        "reportPath": str(report_path.relative_to(ROOT)),
    }
    append_ledger(ledger_row)
    print(f"[emit-fomc] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
