"""JOLTS Job Openings predictor + emitter. `v1-simple-blend`.

Monthly release, ~1st week of month, 10:00 ET by BLS. Value format: level
of job openings in millions (e.g. `7.20M`). Labor-market slack indicator —
Fed watches openings/unemployed ratio closely.

Sub-models:
  - Bloomberg / FF consensus (~150K openings MAE)
  - FRED JTSJOL 3-month trend (~250K MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     JOLTS_RELEASE_DATE, JOLTS_DAYS_OUT, JOLTS_CONSENSUS_M, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-jolts")


from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-jolts")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

# MAE in millions of openings.
MAE = {
    "consensus": 0.15,
    "trend":     0.25,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-jolts] missing env: {key}", file=sys.stderr)
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


def fetch_fred_jolts_trend(api_key: str) -> float | None:
    """3-month mean of JTSJOL (Job Openings level, SA) converted to millions.
    FRED reports as thousands."""
    obs = _fetch_fred_observations(api_key, "JTSJOL", 3)
    if not obs or len(obs) < 3:
        return None
    vals = [float(o["value"]) / 1000.0 for o in obs[:3]]
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
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.05:  # 50K = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta*1000:.0f}K"
    return f"below consensus by {abs(delta)*1000:.0f}K"


def regime_annotation(value: float) -> str:
    """JOLTS regime label. Post-2022 range 7-11M, pre-COVID 5.5-7.5M."""
    if value >= 9.0: return "extremely tight labor demand"
    if value >= 8.0: return "tight labor demand"
    if value >= 7.0: return "moderating labor demand"
    return "softening labor demand"


def format_value(m: float) -> str:
    """JOLTS convention: 2 decimals + M suffix. e.g. '7.20M'."""
    return f"{m:.2f}M"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-jolts")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.2f}M'} | {MAE[name]*1000:.0f}K |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} M", unit="M")
    return f"""# JOLTS Job Openings prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** job openings (level, SA)

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

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~150K MAE) +
FRED JTSJOL 3-month trend (~250K MAE). Short trend window because JOLTS
has been volatile since 2022 (multiple months of 500K+ revisions).

## Why the Fed watches this

Openings/Unemployed ratio (JOLTS Job Openings / U-3 unemployment level) is
Fed Chair Powell's preferred labor-tightness gauge. Ratio >1.5 = extremely
tight; ratio ~1.0 = balanced; ratio <0.8 = slack. Our regime labels use
the openings level directly since the ratio requires waiting for NFP too.

Phase 2 target:
- **Openings/Unemployed ratio** — cross-fetch NFP unemployment level from
  KV, publish ratio alongside headline as a Fed-decision-relevant metric
- **Quits Rate sub-model** — JTSQUL (Quits Level) leads Openings by ~1
  month; add as sub-model
- **Hires vs Separations gap** — JTSHIL - JTSTSL is net employment
  addition; add as sanity check on Openings trend
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "JOLTS_RELEASE_DATE", "JOLTS_DAYS_OUT"):
        require_env(k)

    release = os.environ["JOLTS_RELEASE_DATE"]
    days_out = int(os.environ["JOLTS_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_m("JOLTS_CONSENSUS_M")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_jolts_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-jolts] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("jolts")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-jolts] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-jolts] JOLTS {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma*1000:.0f}K, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.2f}M")
    if trend     is not None: print(f"  trend(3mo): {trend:.2f}M")

    prediction = {
        "eventSlug": f"jolts-{release}",
        "eventTitle": "US JOLTS Job Openings",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/jolts-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"jolts-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-jolts] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-jolts] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
