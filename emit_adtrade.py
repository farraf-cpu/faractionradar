"""Advance Goods Trade Balance predictor. `v1-simple-blend`.

Monthly release, ~last week of month, 08:30 ET by BEA. Goods-only
trade balance for the prior month. Precedes the full Trade Balance
(goods + services) release by ~10 days.

Value format: signed $B (e.g. "-$118.8B" typical, "+$5.0B" rare surplus).

Sub-models:
  - Bloomberg / FF consensus (~$3.0B MAE)
  - FRED BOPGTB (Goods Trade Balance, BOP basis) 3-mo mean anchor (~$5.0B MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     ADTRADE_RELEASE_DATE, ADTRADE_DAYS_OUT, ADTRADE_CONSENSUS, MODEL_VERSION
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

from io_utils import append_ledger as _append_ledger, post_to_worker as _post_to_worker


def append_ledger(payload: dict) -> None:
    _append_ledger(ROOT / "predictions.jsonl", payload)


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    _post_to_worker(url, auth_key, payload, tag="emit-adtrade")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 3.0,
    "anchor":    5.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-adtrade] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_float(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fetch_fred_anchor() -> float | None:
    """3-mo mean of FRED BOPGTB (Trade Balance: Goods, BOP basis), converted
    from millions to billions."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return None
    url = ("https://api.stlouisfed.org/fred/series/observations?"
           f"series_id=BOPGTB&api_key={api_key}&file_type=json"
           "&sort_order=desc&limit=3")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-adtrade] FRED fetch failed: {e}", file=sys.stderr)
        return None
    obs = data.get("observations") or []
    vals = []
    for o in obs:
        v = o.get("value")
        if v and v != ".":
            try:
                vals.append(float(v) / 1000.0)  # millions -> billions
            except ValueError:
                pass
    if len(vals) < 2:
        return None
    return sum(vals) / len(vals)


def blend(consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
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


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.5:
        return "in line with consensus"
    if delta > 0:
        return f"narrower deficit than consensus by ${delta:.1f}B"
    return f"wider deficit than consensus by ${abs(delta):.1f}B"


def regime_annotation(value: float) -> str:
    """Goods-only deficit runs wider than combined trade balance. Post-COVID
    range roughly -$70B to -$130B."""
    if value >= -80:   return "narrower goods deficit"
    if value >= -110:  return "typical goods deficit"
    if value >= -130:  return "wide goods deficit"
    return "extreme goods deficit"


def format_value(b: float) -> str:
    return f"{'+' if b >= 0 else '-'}${abs(b):.1f}B"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-adtrade")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else format_value(v)} | ${MAE[name]:.1f}B |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} B", unit="B")
    return f"""# Advance Goods Trade Balance prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** advance goods trade balance

- Regime: {regime_annotation(point)}
- 68% CI: [{format_value(point - sigma)}, {format_value(point + sigma)}] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} B)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{format_value(point - 2*sigma)}, {format_value(point + 2*sigma)}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
BOPGTB 3-month mean (Goods Trade Balance, Balance of Payments basis).

## Positioning

Goods-only trade balance released ~10 days ahead of the full Trade
Balance report. Advance report → market-moving import/export mix
signal for GDP nowcasts; the goods-services split lands with the
full report. Leading indicator on Q/Q GDP net-exports contribution.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** — first ship.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "ADTRADE_RELEASE_DATE", "ADTRADE_DAYS_OUT"):
        require_env(k)

    release = os.environ["ADTRADE_RELEASE_DATE"]
    days_out = int(os.environ["ADTRADE_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("ADTRADE_CONSENSUS")
    anchor = fetch_fred_anchor()

    if consensus is None and anchor is None:
        print("[emit-adtrade] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("adtrade")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-adtrade] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-adtrade] AdvGoodsTrade {release} T-{days_out}: {format_value(point)} "
          f"(sigma ${sigma:.1f}B, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {format_value(consensus)}")
    if anchor    is not None: print(f"  anchor:     {format_value(anchor)}")

    prediction = {
        "eventSlug": f"adtrade-{release}",
        "eventTitle": "US Advance Goods Trade Balance",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/adtrade-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"adtrade-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-adtrade] wrote {report_path.relative_to(ROOT)}")

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
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit-adtrade] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
