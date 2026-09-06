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

from io_utils import append_ledger as _append_ledger, post_to_worker as _post_to_worker


def append_ledger(payload: dict) -> None:
    _append_ledger(ROOT / "predictions.jsonl", payload)


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    _post_to_worker(url, auth_key, payload, tag="emit-trade")


from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-trade")


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


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-trade")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else format_value(v)} | ${MAE[name]:.1f}B |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} B", unit="B")
    return f"""# Trade Balance prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** trade balance (goods + services, SA)

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
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("trade")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-trade] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
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
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
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
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit-trade] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
