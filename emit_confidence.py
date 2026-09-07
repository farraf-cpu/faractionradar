"""Consumer Confidence (Conference Board) predictor + emitter. `v1-simple-blend`.

Monthly, last Tuesday of month, 10:00 ET by The Conference Board. Value
format: index level normalized to 1985=100, typical range 60-140. Similar
to ISM PMI, this index is proprietary to Conference Board so we can't pull
a FRED trend cleanly. v1 ships with consensus + naive last-known anchor.

Sub-models:
  - Bloomberg / FF consensus (~2.0 index points MAE)
  - Last-known anchor (~4.0 index points MAE — naive persistence)

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     CONFIDENCE_RELEASE_DATE, CONFIDENCE_DAYS_OUT,
     CONFIDENCE_CONSENSUS, CONFIDENCE_ANCHOR, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-confidence")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

# Index-points MAE. Consensus MAE on Consumer Confidence is ~2 pts —
# analysts triangulate from University of Michigan preliminary + weekly
# sentiment surveys. Anchor is naive persistence — wider.
MAE = {
    "consensus": 2.0,
    "anchor":    4.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-confidence] missing env: {key}", file=sys.stderr)
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


def blend(consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if anchor is not None:
        parts.append(("anchor", anchor, MAE["anchor"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    return inverse_variance_combine(parts)


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.5:  # 0.5 index pts = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    """Consumer Confidence regime. Post-COVID range 75-135."""
    if value >= 120: return "elevated confidence"
    if value >= 100: return "healthy confidence"
    if value >= 85:  return "cautious confidence"
    return "weak confidence"


def format_value(v: float) -> str:
    """CB Confidence convention: 1 decimal. e.g. '104.5'."""
    return f"{v:.1f}"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-confidence")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pts", unit="pts")
    return f"""# Consumer Confidence prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** index (1985 = 100)

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

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
Conference Board's index is proprietary (analogous to ISM PMI) so no
FRED trend sub-model in v1. Same architecture as ISM Manufacturing/Services
predictors.

## Phase 2 target

- **University of Michigan Consumer Sentiment (UMCSENT)** — FRED-published
  free, releases mid-month (preliminary) and end-of-month (revised),
  correlates ~0.75 with Conference Board's Consumer Confidence
- **Weekly consumer sentiment surveys** — Bloomberg Weekly Consumer
  Comfort, Redfin Homebuyer Demand — build weighted composite as leading
  indicator for CB
- **Sub-index decomposition** — Present Situation vs Expectations
  components diverge in inflection months; publish both

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 15th event covered.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "CONFIDENCE_RELEASE_DATE", "CONFIDENCE_DAYS_OUT"):
        require_env(k)

    release = os.environ["CONFIDENCE_RELEASE_DATE"]
    days_out = int(os.environ["CONFIDENCE_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("CONFIDENCE_CONSENSUS")
    anchor = parse_float("CONFIDENCE_ANCHOR")

    if consensus is None and anchor is None:
        print("[emit-confidence] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("confidence")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-confidence] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-confidence] Confidence {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.1f}")
    if anchor    is not None: print(f"  anchor:     {anchor:.1f}")

    prediction = {
        "eventSlug": f"confidence-{release}",
        "eventTitle": "US CB Consumer Confidence",
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
                                consensus, anchor, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"confidence-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-confidence] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-confidence] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
