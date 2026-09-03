"""Trade Balance predictor + emitter. `v1-simple-blend`.

Monthly release, ~1st week of month, 08:30 ET by BEA + Census. Value format:
US trade deficit in $ billions (typically negative, e.g. "-$78.5B"). Feeds
into GDP nowcasting via net-exports component.

Sub-models:
  - Bloomberg / FF consensus (~$3B MAE on headline)
  - FRED BOPGSTB 3-month trend (~$4B MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     TRADE_RELEASE_DATE, TRADE_DAYS_OUT, TRADE_CONSENSUS_B, MODEL_VERSION
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

# MAE in billions of USD.
MAE = {
    "consensus": 3.0,
    "trend":     4.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-trade] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_b(env_key: str) -> float | None:
    """Env value is a signed number in billions (e.g. '-78.5')."""
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={urllib.parse.quote(series_id)}"
           f"&api_key={urllib.parse.quote(api_key)}"
           f"&file_type=json&sort_order=desc&limit={limit}")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-trade] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_trade_trend(api_key: str) -> float | None:
    """3-month mean of BOPGSTB (Trade Balance: Goods and Services), converted
    from millions to billions."""
    obs = _fetch_fred_observations(api_key, "BOPGSTB", 3)
    if not obs or len(obs) < 3:
        return None
    vals_b = [float(o["value"]) / 1000.0 for o in obs[:3]]
    return sum(vals_b) / len(vals_b)


def blend(consensus: float | None,
          trend: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if trend is not None:
        parts.append(("trend", trend, MAE["trend"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.5:  # $0.5B = noise
        return "in line with consensus"
    # For trade balance, "wider" = more negative (deeper deficit)
    if delta > 0:
        return f"narrower deficit than consensus by ${delta:.1f}B"
    return f"wider deficit than consensus by ${abs(delta):.1f}B"


def regime_annotation(value: float) -> str:
    """Trade deficit regime. Post-COVID US trade deficit range -$50B to -$100B."""
    if value >= -60:  return "narrower deficit"
    if value >= -80:  return "typical deficit"
    if value >= -100: return "wide deficit"
    return "extreme deficit"


def format_value(b: float) -> str:
    """Trade convention: signed, $B. e.g. '-$78.5B' or '+$5.0B' (rare surplus)."""
    return f"{'+' if b >= 0 else '-'}${abs(b):.1f}B"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else format_value(v)} | ${MAE[name]:.1f}B |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# Trade Balance prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** trade balance (goods + services, SA)

- Regime: {regime_annotation(point)}
- 68% CI: [{format_value(point - sigma)}, {format_value(point + sigma)}]
- 95% CI: [{format_value(point - 2*sigma)}, {format_value(point + 2*sigma)}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~$3B MAE) +
FRED BOPGSTB 3-month trend (~$4B MAE). Trade balance is a component of
GDP (net exports contribution) so this predictor also feeds any Phase 2
GDPNow-style multi-signal work.

Phase 2 targets:
- **Advance Goods Trade Balance** — separate slug (goods-only, released
  ~1 week before Combined). Leads Combined by directional signal
- **Petroleum trade balance carve-out** — oil-price-driven swings distort
  headline. Split petroleum vs ex-petroleum
- **Dollar index cross** — DXY 3-month change correlates ~-0.4 with
  headline trade balance (stronger dollar = wider deficit); add as
  cross-check signal
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
            print(f"[emit-trade] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-trade] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "TRADE_RELEASE_DATE", "TRADE_DAYS_OUT"):
        require_env(k)

    release = os.environ["TRADE_RELEASE_DATE"]
    days_out = int(os.environ["TRADE_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_b("TRADE_CONSENSUS_B")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_trade_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-trade] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-trade] Trade {release} T-{days_out}: {format_value(point)} "
          f"(sigma ${sigma:.1f}B, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {format_value(consensus)}")
    if trend     is not None: print(f"  trend(3mo): {format_value(trend)}")

    prediction = {
        "eventSlug": f"trade-{release}",
        "eventTitle": "US Trade Balance",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma, 1), round(point + sigma, 1)],
            "ci95": [round(point - 2 * sigma, 1), round(point + 2 * sigma, 1)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/trade-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"trade-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-trade] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-trade] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
