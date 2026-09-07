"""Existing Home Sales predictor + emitter. `v1.1-simple-blend`.

Monthly release, ~20th-24th of month, 10:00 ET by NAR. Value format:
annualized rate in millions (e.g. `4.05M`). Housing-market activity gauge
that leads Housing Starts by 1-2 months on inflection.

Sub-models:
  - Bloomberg / FF consensus (~50K MAE on annualized rate)
  - FRED EXHOSLUSM495S 3-month trend (~80K MAE)
  - FRED MORTGAGE30US mortgage-rate shock (~100K MAE — Freddie Mac 30-yr
    fixed 2-month rate change applied to trend baseline as sensitivity
    adjustment. Rate up → sales down after 2mo lag (-0.6 correlation).
    Conservative pre-empirical weight; graceful fallback on FRED failure.)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     EXISTING_RELEASE_DATE, EXISTING_DAYS_OUT, EXISTING_CONSENSUS_M, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-existing")


from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-existing")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus":       0.05,   # 50K annualized
    "trend":           0.08,   # 80K annualized
    "mortgage_shock":  0.10,   # 100K annualized, conservative pre-empirical
}

# Mortgage-rate sensitivity: %-response in existing sales per 100bp of
# mortgage rate change over a 2-month window. Historical -0.6 correlation
# translates to roughly 0.5% sales response per 100bp rate move. Sign is
# negative (rate up -> sales down after 2mo lag).
MORTGAGE_SENSITIVITY = -0.005


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-existing] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_m(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fetch_fred_existing_trend(api_key: str) -> float | None:
    """3-month mean of EXHOSLUSM495S (Existing Home Sales, SA annualized).
    FRED reports in thousands — convert to millions."""
    obs = _fetch_fred_observations(api_key, "EXHOSLUSM495S", 3)
    if not obs or len(obs) < 3:
        return None
    vals = [float(o["value"]) / 1000.0 for o in obs[:3]]
    return sum(vals) / len(vals)


def fetch_mortgage_shock(api_key: str, trend_baseline: float | None) -> float | None:
    """Apply MORTGAGE30US 2-month rate change to the trend baseline as a
    mortgage-shock sub-model estimate. Returns None if MORTGAGE30US fetch
    fails or the trend baseline is unavailable — mortgage signal is only
    meaningful as a sensitivity adjustment on the current sales trend.

    Mechanism: Freddie Mac 30-year fixed (weekly series) has a
    documented ~-0.6 correlation with existing home sales at a 2-month
    lag. Rising rates lock potential sellers into low-rate mortgages
    (lock-in effect) and price out buyers on affordability."""
    if trend_baseline is None:
        return None
    obs = _fetch_fred_observations(api_key, "MORTGAGE30US", 9)
    if not obs or len(obs) < 9:
        return None
    try:
        rates = [float(o["value"]) for o in obs[:9]]
    except (ValueError, KeyError):
        return None
    # Recent rate (avg of last 2 weekly obs) vs 8-week-lagged rate
    # (avg of oldest 2 obs). Both in percent (e.g. 6.85).
    recent = (rates[0] + rates[1]) / 2.0
    lagged = (rates[7] + rates[8]) / 2.0
    rate_change_bp = (recent - lagged) * 100.0  # percent -> basis points
    return trend_baseline * (1.0 + MORTGAGE_SENSITIVITY * rate_change_bp)


def blend(consensus: float | None,
          trend: float | None,
          mortgage_shock: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if trend is not None:
        parts.append(("trend", trend, MAE["trend"]))
    if mortgage_shock is not None:
        parts.append(("mortgage_shock", mortgage_shock, MAE["mortgage_shock"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    return inverse_variance_combine(parts)


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.02:  # 20K = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta*1000:.0f}K"
    return f"below consensus by {abs(delta)*1000:.0f}K"


def regime_annotation(value: float) -> str:
    """Existing home sales regime. Historical range 3-7M annualized."""
    if value >= 5.5: return "hot resale market"
    if value >= 4.5: return "healthy resale market"
    if value >= 3.8: return "slow resale market"
    return "frozen resale market"


def format_value(m: float) -> str:
    """Existing homes convention: 2 decimals + M suffix. e.g. '4.05M'."""
    return f"{m:.2f}M"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-existing")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, mortgage_shock: float | None,
                    used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.2f}M'} | {MAE[name]*1000:.0f}K |"
        for name, v in (("consensus", consensus), ("trend", trend), ("mortgage_shock", mortgage_shock))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} M", unit="M")
    return f"""# Existing Home Sales prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** annualized existing home sales (SA)

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:.2f}M, {point + sigma:.2f}M] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} M)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:.2f}M, {point + 2*sigma:.2f}M]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 3 sub-models —
consensus (~50K MAE) + FRED EXHOSLUSM495S 3-month trend (~80K MAE) +
FRED MORTGAGE30US 2-month rate-shock adjustment (~100K MAE, conservative
pre-empirical). Existing home sales tracks the resale market — different
signal than Housing Starts (new construction).

Mortgage-shock formula: `trend * (1 + MORTGAGE_SENSITIVITY * rate_change_bp)`
where MORTGAGE_SENSITIVITY = -0.005 (0.5% sales response per 100bp,
sign negative = rate up → sales down after 2mo lag). Empirical MAE
auto-tune replaces prior weight once N>=5 resolutions.

## Phase 2 targets

- **Pending Home Sales cross** — NAR Pending Home Sales leads Existing
  by 1-2 months as a same-shop earnings-like leading indicator
- **Regional decomposition** — Northeast/Midwest/South/West follow
  different seasonal patterns; South is ~45% of national

## Change log

- **v1.1-simple-blend (2026-09-07)** — added FRED MORTGAGE30US 2-month
  rate-change as mortgage-shock sub-model. Sensitivity -0.005 per bp is
  conservative pre-empirical; falls through cleanly on FRED failure.
- **v1-simple-blend (2026-09-03)** — first ship. 17th event covered.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "EXISTING_RELEASE_DATE", "EXISTING_DAYS_OUT"):
        require_env(k)

    release = os.environ["EXISTING_RELEASE_DATE"]
    days_out = int(os.environ["EXISTING_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1.1-simple-blend")

    consensus = parse_m("EXISTING_CONSENSUS_M")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_existing_trend(fred_key) if fred_key else None
    mortgage_shock = fetch_mortgage_shock(fred_key, trend) if fred_key else None

    if consensus is None and trend is None and mortgage_shock is None:
        print("[emit-existing] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend, mortgage_shock)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("existing")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-existing] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-existing] Existing {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma*1000:.0f}K, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus       is not None: print(f"  consensus:              {consensus:.2f}M")
    if trend           is not None: print(f"  trend (EXHOSLUSM495S):  {trend:.2f}M")
    if mortgage_shock  is not None: print(f"  mortgage (MORTGAGE30US):{mortgage_shock:.2f}M")

    prediction = {
        "eventSlug": f"existing-{release}",
        "eventTitle": "US Existing Home Sales",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma, 2), round(point + sigma, 2)],
            "ci95": [round(point - 2 * sigma, 2), round(point + 2 * sigma, 2)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, mortgage_shock, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"existing-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-existing] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-existing] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
