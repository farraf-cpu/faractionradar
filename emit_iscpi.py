"""Swiss CPI predictor. v1-simple-blend.

Statistics Iceland publishes monthly CPI y/y
~1 week after reference month at 08:30 CET (07:30 UTC winter).
SARB targets 3-6% CPI y/y band (+/- 1pp).

Consensus-only for v1: FRED's CPALTT01ISM659N is stale (last obs
2025-03, usable but slow-moving). Statistics Iceland Statistical Portal API
integration deferred to v1.1.

Value format: y/y %-change (e.g. "+2.9%").
Sub-models:
  - FF consensus (~0.15pp MAE - primary signal)

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     ISCPI_RELEASE_DATE, ISCPI_DAYS_OUT, ISCPI_CONSENSUS, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-iscpi")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 0.15,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-iscpi] missing env: {key}", file=sys.stderr)
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


def blend(consensus: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    return inverse_variance_combine(parts)


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.1:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def regime_annotation(value: float) -> str:
    if value >= 3.0:  return "hot JP inflation (RBNZ hawkish pressure)"
    if value >= 2.0:  return "above RBNZ target"
    if value >= 1.5:  return "near RBNZ target"
    if value >= 0.5:  return "below target"
    return "deflationary / disinflation"


def format_value(v: float) -> str:
    return f"{v:+.1f}%"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-iscpi")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = f"| consensus | {'-' if consensus is None else f'{consensus:+.2f}%'} | {MAE['consensus']:.2f}pp |"
    prior_mae_used = MAE.get('consensus', min(MAE.values()))
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pp", unit="pp")
    return f"""# JP CPI prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** y/y NZ CPI CPI

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} pp)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 24 (ISK expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by Statistics Iceland ~19th-27th of
following month at 10:45 ISKT.

## Caveats

FRED coverage for Japan CPI is dead — an Statistics Iceland Statistics Iceland Statistical Portal API integration
(hagstofa.is, free with registration) would give a real trend
anchor. Phase 24.1 target.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Phase 24 ISK expansion. Consensus-only pending Statistics Iceland Statistics Iceland Statistical Portal API.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "ISCPI_RELEASE_DATE", "ISCPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["ISCPI_RELEASE_DATE"]
    days_out = int(os.environ["ISCPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("ISCPI_CONSENSUS")

    if consensus is None:
        print("[emit-iscpi] consensus missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("iscpi")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-iscpi] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-iscpi] ISCPI {release} T-{days_out}: {format_value(point)} y/y "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")

    prediction = {
        "eventSlug": f"iscpi-{release}",
        "eventTitle": "NZ CPI CPI y/y",
        "country": "ISK",
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
                                consensus, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"iscpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-iscpi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-iscpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
