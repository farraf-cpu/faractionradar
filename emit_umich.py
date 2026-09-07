"""UMich Consumer Sentiment (Preliminary) predictor + emitter. `v1-simple-blend`.

Monthly release, ~mid-month (2nd Friday), 10:00 ET by University of Michigan
Survey of Consumers. Value format: index level (typical 60-100). Unlike CB
Consumer Confidence, this series IS on FRED (UMCSENT is publicly available
under license). Correlates ~0.75 with CB Confidence but releases 2-3 weeks
earlier — often a leading indicator.

Sub-models:
  - Bloomberg / FF consensus (~1.5 index points MAE)
  - FRED UMCSENT 3-month trend (~2.5 pts MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     UMICH_RELEASE_DATE, UMICH_DAYS_OUT, UMICH_CONSENSUS, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-umich")


from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-umich")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 1.5,
    "trend":     2.5,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-umich] missing env: {key}", file=sys.stderr)
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


def fetch_fred_umich_trend(api_key: str) -> float | None:
    """3-month mean of UMCSENT (Michigan Consumer Sentiment, monthly)."""
    obs = _fetch_fred_observations(api_key, "UMCSENT", 3)
    if not obs or len(obs) < 3:
        return None
    vals = [float(o["value"]) for o in obs[:3]]
    return sum(vals) / len(vals)


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
    if abs(delta) < 0.3:  # ~0.3 pts = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    """UMich sentiment regime. Historical range 50-110."""
    if value >= 90: return "strong sentiment"
    if value >= 75: return "moderate sentiment"
    if value >= 60: return "weak sentiment"
    return "recession-level sentiment"


def format_value(v: float) -> str:
    """UMich convention: 1 decimal. e.g. '72.5'."""
    return f"{v:.1f}"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-umich")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pts", unit="pts")
    return f"""# UMich Consumer Sentiment prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** index

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:.1f}, {point + sigma:.1f}] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} pts)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:.1f}, {point + 2*sigma:.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~1.5 pts MAE) +
FRED UMCSENT 3-month trend (~2.5 pts MAE). Unlike CB Consumer Confidence,
UMCSENT is freely published on FRED — enables real trend sub-model.

## Relationship to CB Consumer Confidence

Correlates ~0.75 with CB Confidence but releases 2-3 weeks earlier
(preliminary comes mid-month vs CB's last Tuesday). Often a leading
indicator for CB Confidence direction changes.

## Phase 2 targets

- **Inflation Expectations sub-index** — UMich publishes 1-year and 5-year
  inflation expectations as sub-indices. Fed watches these; separate slug
  in Phase 2
- **Preliminary vs Revised split** — Revised release comes end-of-month
  with sample doubled. Add separate slug `umich-revised-<date>`
- **Weekly sentiment cross** — Bloomberg Weekly Consumer Comfort as high-
  frequency leading input

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 19th event covered.
  Covers Preliminary only; Revised is Phase 2.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "UMICH_RELEASE_DATE", "UMICH_DAYS_OUT"):
        require_env(k)

    release = os.environ["UMICH_RELEASE_DATE"]
    days_out = int(os.environ["UMICH_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("UMICH_CONSENSUS")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_umich_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-umich] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("umich")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-umich] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-umich] UMich {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.1f}")
    if trend     is not None: print(f"  trend(3mo): {trend:.1f}")

    prediction = {
        "eventSlug": f"umich-{release}",
        "eventTitle": "US UMich Consumer Sentiment (Preliminary)",
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
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"umich-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-umich] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-umich] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
