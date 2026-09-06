"""Initial Jobless Claims predictor + emitter. `v1-simple-blend`.

Weekly release. Every Thursday 08:30 ET by DOL. Value format is a level
in thousands (e.g. `220K`, `245K`). Bigger high-frequency signal on labor
market than monthly NFP — hedge funds trade this print.

Sub-models:
  - Bloomberg / FF consensus (~10K claims MAE — analysts get most of the
    signal from prior week's actual)
  - FRED ICSA 4-week trend (~14K MAE — mean-reverting anchor)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     CLAIMS_RELEASE_DATE, CLAIMS_DAYS_OUT, CLAIMS_CONSENSUS_K, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-claims")


from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-claims")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

# MAE in thousands of claims (K). Consensus MAE ~10K is well-established
# for weekly Initial Claims — the series is smooth enough that consensus
# anchors well. Trend MAE (4-week average) wider because it doesn't react
# to sudden inflection weeks (hurricanes, strikes).
MAE = {
    "consensus": 10.0,
    "trend":     14.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-claims] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_k(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fetch_fred_claims_trend(api_key: str) -> float | None:
    """4-week mean of ICSA (Initial Claims, SA) in thousands.
    FRED reports ICSA as raw number of claims — divide by 1000 for K."""
    obs = _fetch_fred_observations(api_key, "ICSA", 4)
    if not obs or len(obs) < 4:
        return None
    vals_k = [float(o["value"]) / 1000.0 for o in obs[:4]]
    return sum(vals_k) / len(vals_k)


def blend(consensus: float | None,
          trend: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if trend is not None:
        parts.append(("trend", trend, MAE["trend"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    return inverse_variance_combine(parts)


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 3:  # ~3K claims = noise on weekly
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.0f}K"
    return f"below consensus by {abs(delta):.0f}K"


def regime_annotation(value: float) -> str:
    """Loose labor-market regime label. Historical ranges post-COVID."""
    if value < 200: return "very tight labor market"
    if value < 240: return "tight labor market"
    if value < 280: return "softening labor market"
    return "deteriorating labor market"


def format_value(k: float) -> str:
    """Claims convention: whole thousand + K suffix. e.g. '225K'."""
    return f"{round(k)}K"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-claims")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.0f}K'} | {MAE[name]:.0f}K |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.1f} K", unit="K")
    return f"""# Initial Jobless Claims prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** claims (initial, seasonally adjusted)

- Regime: {regime_annotation(point)}
- 68% CI: [{round(point - sigma)}K, {round(point + sigma)}K] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.1f}K)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{round(point - 2*sigma)}K, {round(point + 2*sigma)}K]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "CLAIMS_RELEASE_DATE", "CLAIMS_DAYS_OUT"):
        require_env(k)

    release = os.environ["CLAIMS_RELEASE_DATE"]
    days_out = int(os.environ["CLAIMS_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_k("CLAIMS_CONSENSUS_K")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_claims_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-claims] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("claims")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-claims] sigma auto-tuned: prior={prior_sigma:.3f}pp -> empirical={sigma:.3f}pp")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-claims] Claims {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f}K, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.0f}K")
    if trend     is not None: print(f"  trend(4wk): {trend:.0f}K")

    prediction = {
        "eventSlug": f"claims-{release}",
        "eventTitle": "US Initial Jobless Claims",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma), round(point + sigma)],
            "ci95": [round(point - 2 * sigma), round(point + 2 * sigma)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/claims-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"claims-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-claims] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-claims] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
