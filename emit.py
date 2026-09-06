"""GHA emission wrapper — runs the predictor, POSTs to the calendar-worker,
writes a versioned .md report, and appends to predictions.jsonl.

Local dev: this is NOT for local runs. Use `python run.py` for that. This
script only makes sense when the GHA secrets are populated.

Environment (set by GHA workflow):
  FRED_API_KEY          — read by src/fred_fetch.py during the model run
  UPLOAD_AUTH_KEY       — used in POST body to authenticate to /upload
  CALENDAR_WORKER_URL   — e.g. https://faractionradar-calendar.faractionradar.workers.dev
  NFP_RELEASE_DATE      — ISO date of the NFP print this run is targeting (YYYY-MM-DD)
  NFP_DAYS_OUT          — integer: 7, 4, 3, 2, or 1 (which cadence slot)
  MODEL_VERSION         — pinned string, e.g. "v1-bayesian-blend"

Emits (all committed by the workflow after this script exits):
  reports/YYYY-MM/nfp-t-<N>.md      — full human-readable model output
  predictions.jsonl                  — one line per prediction, all-history ledger
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from io_utils import append_ledger as _append_ledger, post_to_worker as _post_to_worker


def append_ledger(payload: dict) -> None:
    _append_ledger(ROOT / "predictions.jsonl", payload)


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    _post_to_worker(url, auth_key, payload, tag="emit")



from mae_utils import (
    fetch_empirical_mae as _fetch_empirical_mae,
    build_empirical_mae_section as _build_empirical_mae_section,
    auto_tune_sigma,
)


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    """Thin wrapper — keeps existing tests + call sites working."""
    return _fetch_empirical_mae(slug_prefix, tag="emit")


def build_empirical_mae_section(obs: dict | None, prior_mae_str: str) -> str:
    """NFP uses jobs-count units ('K') for empirical MAE display."""
    return _build_empirical_mae_section(obs, prior_mae_str, unit="K")


from mae_utils import (
    parse_market_ladder_env,
    survival_from_ladder as _shared_survival,
)


def parse_market_ladder() -> list[tuple[float, float]] | None:
    return parse_market_ladder_env("NFP_MARKET_LADDER", tag="emit")


def survival_from_ladder(x: float, rungs: list[tuple[float, float]]) -> float:
    return _shared_survival(x, rungs)


def compute_market_outcome_distribution(ladder: list[tuple[float, float]]) -> dict:
    """Discretize the KXUSNFP ladder into 6 jobs-count buckets covering
    the typical NFP range. Ladder thresholds arrive in RAW jobs (not K),
    so bucket edges are in raw jobs too. Renormalized to sum 1."""
    # Bucket edges in raw jobs: <=25K, 25-75, 75-125, 125-175, 175-225, 225K+
    edges = [25_000, 75_000, 125_000, 175_000, 225_000]
    keys = ["<=25K", "25-75K", "75-125K", "125-175K", "175-225K", "225K+"]
    dist: dict = {}
    dist[keys[0]] = 1.0 - survival_from_ladder(edges[0], ladder)
    for i in range(len(edges) - 1):
        dist[keys[i + 1]] = (survival_from_ladder(edges[i], ladder)
                             - survival_from_ladder(edges[i + 1], ladder))
    dist[keys[-1]] = survival_from_ladder(edges[-1], ladder)
    for k in list(dist.keys()):
        dist[k] = round(max(0.0, min(1.0, dist[k])), 3)
    total = sum(dist.values())
    if total > 0:
        for k in dist:
            dist[k] = round(dist[k] / total, 3)
    modal = max(dist.items(), key=lambda x: x[1])[0]
    dist["modal"] = modal
    dist["source"] = "kalshi-ladder"
    return dist

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

REQUIRED_ENV = ["UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "NFP_RELEASE_DATE", "NFP_DAYS_OUT"]


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit] missing required env var: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def format_our_call(result: dict, release_date: str, model_version: str) -> dict:
    """Map the predictor's internal `result` dict to CalendarEvent.prediction.ourCall
    per ROADMAP §4.1. Model logic is untouched — this is pure shape mapping."""
    blended = result["blended"]
    rmse = result["blended_rmse"]
    return {
        "value": f"{blended:+.0f}K",
        "lean": result["lean"],
        "ci68": [round(blended - rmse), round(blended + rmse)],
        "ci95": [round(blended - 2 * rmse), round(blended + 2 * rmse)],
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
    }


def format_grand_median(result: dict) -> dict:
    """7 sub-models feed the grand median — see docs/nfp-model-card.md."""
    return {
        "value": f"{result['grand_median']:+.0f}K",
        "sourceCount": 7,
    }


def build_market_dist_section(dist: dict | None) -> str:
    """Render the market outcome distribution over the 6 jobs-count buckets."""
    if not dist:
        return ""
    modal = dist.get("modal")
    src = dist.get("source", "unknown")
    order = ["<=25K", "25-75K", "75-125K", "125-175K", "175-225K", "225K+"]
    rows = []
    for k in order:
        v = dist.get(k)
        if not isinstance(v, (int, float)):
            continue
        marker = " **(modal)**" if k == modal else ""
        rows.append(f"| {k} | {v*100:.1f}%{marker} |")
    if not rows:
        return ""
    body = "\n".join(rows)
    return f"""
## Market outcome distribution (source: `{src}`)

| Jobs count | Probability |
|------------|-------------|
{body}

"""


def build_report_md(result: dict, release_date: str, days_out: int, model_version: str,
                    market_dist: dict | None = None,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (blended RMSE)",
                    prior_rmse: float | None = None) -> str:
    b = result["blended"]
    r = result["blended_rmse"]
    pm_note = " (stale, see caveat)" if result.get("pred_markets_stale") else ""
    caveat_section = ""
    if result.get("pred_markets_stale"):
        caveat_section = (
            "\n## Caveats\n\n"
            "The prediction-markets input is a hardcoded July baseline pending"
            " Kalshi ticker-mapping verification (Phase 1.5). Consensus is live"
            " from ForexFactory; the point estimate is anchored to live"
            " consensus + first-print model output. The markets weight will"
            " refresh once real ticker mapping lands.\n"
        )
    dist_section = build_market_dist_section(market_dist)
    # Best sub-model MAE on NFP = prediction markets (~40K)
    empirical_section = build_empirical_mae_section(empirical_mae, "~40 K (best sub-model, markets)")
    return f"""# NFP prediction — target {release_date} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{b:+.0f}K jobs**

- 68% CI: [{b-r:+.0f}, {b+r:+.0f}] K · sigma source: {sigma_source}{f" (prior was {prior_rmse:.0f}K)" if prior_rmse is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{b-2*r:+.0f}, {b+2*r:+.0f}] K
- Lean vs consensus: {result['lean']}
{caveat_section}{dist_section}{empirical_section}## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| Bloomberg consensus       | {result['consensus']:+7.0f} K | ~55 K |
| Prediction markets (avg)  | {result['pred_markets']:+7.0f} K{pm_note} | ~40 K |
| ML ensemble (revised)     | {result['ml_ensemble']:+7.0f} K | — |
| First-print ensemble      | {result['first_print_ensemble']:+7.0f} K | — |
| Bridge models median      | {result['bridge_median']:+7.0f} K | — |
| Sector decomposition (11) | {result['sector_pred']:+7.0f} K | — |
| Grand median (all models) | {result['grand_median']:+7.0f} K | — |
| **Blended (Bayesian)**    | **{b:+7.0f} K** | — |
"""


def main() -> None:
    for key in REQUIRED_ENV:
        require_env(key)

    release_date = os.environ["NFP_RELEASE_DATE"]
    days_out = int(os.environ["NFP_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-bayesian-blend")
    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    auth_key = os.environ["UPLOAD_AUTH_KEY"]

    from run import main as run_predictor
    result = run_predictor(refresh_data=True)

    # Empirical MAE auto-tune (shared via mae_utils.auto_tune_sigma).
    empirical_mae = fetch_empirical_mae("nfp")
    prior_rmse = float(result.get("blended_rmse") or 0)
    new_sigma, sigma_source = auto_tune_sigma(prior_rmse, empirical_mae)
    if sigma_source.startswith("empirical"):
        result["blended_rmse"] = new_sigma
        # NFP-specific label — auto_tune_sigma returns "prior (inverse-MAE)"
        # by default which reads awkwardly on NFP where the prior is the
        # bayesian blend's RMSE. No-op when threshold not met.
        print(f"[emit] sigma auto-tuned: prior={prior_rmse:.1f}K -> empirical={new_sigma:.1f}K")
    elif sigma_source == "prior (inverse-MAE)":
        sigma_source = "prior (blended RMSE)"

    our_call = format_our_call(result, release_date, model_version)
    ladder = parse_market_ladder()
    market_dist: dict | None = None
    if ladder:
        market_dist = compute_market_outcome_distribution(ladder)
        our_call["outcomeDistribution"] = market_dist
        print(f"[emit] kalshi ladder outcome dist: {market_dist}")

    prediction = {
        "eventSlug": f"nfp-{release_date}",
        "eventTitle": "US Non-Farm Payrolls",
        "country": "USD",
        "releaseDate": release_date,
        "daysOut": days_out,
        "ourCall": our_call,
        "grandMedian": format_grand_median(result),
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/nfp-model-card.md",
    }
    if result.get("pred_markets_stale"):
        prediction["caveat"] = (
            "prediction-market input is a hardcoded July baseline pending Kalshi"
            " ticker verification (Phase 1.5). Consensus is live from ForexFactory."
        )

    report_md = build_report_md(result, release_date, days_out, model_version,
                                market_dist=market_dist,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_rmse=prior_rmse)
    year_month = release_date[:7]
    report_path = ROOT / "reports" / year_month / f"nfp-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit] wrote {report_path.relative_to(ROOT)}")

    ledger_row = {
        "publishedAt": prediction["ourCall"]["publishedAt"],
        "eventSlug": prediction["eventSlug"],
        "daysOut": days_out,
        "modelVersion": model_version,
        "ourCall": prediction["ourCall"]["value"],
        "ci68": prediction["ourCall"]["ci68"],
        "grandMedian": prediction["grandMedian"]["value"],
        "reportPath": str(report_path.relative_to(ROOT)),
    }
    if isinstance(market_dist, dict):
        modal = market_dist.get("modal")
        source = market_dist.get("source")
        if modal:
            ledger_row["modalOutcome"] = modal
        if source:
            ledger_row["outcomeSource"] = source
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit] appended predictions.jsonl")

    post_to_worker(worker_url, auth_key, prediction)


if __name__ == "__main__":
    main()
