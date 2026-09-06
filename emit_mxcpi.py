"""MX CPI predictor. v1.1-inegi.

INEGI publishes monthly INPC (Índice Nacional de Precios al Consumidor)
y/y ~2nd week of following month at 06:00 CST (12:00 UTC winter).
Banxico targets 3% CPI y/y (+/- 1pp).

v1.1 adds INEGI BIE trend anchor sub-model. FRED's CPALTT01MXM659N is
stale (last obs 2025-03); INEGI is the authoritative Mexican
statistics portal (inegi.org.mx/servicios/api_indicadores.html).

Activate: set INEGI_TOKEN env var to a free INEGI API token
(register at https://www.inegi.org.mx/app/api/indicadores/interfaz.html).
When token absent, falls back to consensus-only (v1 behavior).

Value format: y/y %-change (e.g. "+3.5%").
Sub-models:
  - FF consensus (~0.15pp MAE)
  - INEGI INPC y/y 3-mo mean (~0.25pp MAE) [opt-in]

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     MXCPI_RELEASE_DATE, MXCPI_DAYS_OUT, MXCPI_CONSENSUS, MODEL_VERSION
     INEGI_TOKEN (optional, activates INEGI trend anchor)
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
    _post_to_worker(url, auth_key, payload, tag="emit-mxcpi")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 0.15,
    "trend":     0.25,   # INEGI INPC y/y 3-mo mean
}

# INEGI BIE indicator ID 628194 = INPC general y/y variation, monthly.
# BIE (Banco de Información Económica) catalog reference:
# https://www.inegi.org.mx/temas/inpc/
# Path: /INDICATOR/es/0700/false/BIE/2.0/{TOKEN}?type=json
# 0700 = last observations; BIE = source; 2.0 = API version.
INEGI_INDICATOR_INPC_YOY = "628194"


def fetch_inegi_trend() -> float | None:
    """3-mo mean of MX INPC y/y from INEGI BIE.
    Returns None if INEGI_TOKEN env not set or API errors.
    Requires free API token registered at inegi.org.mx."""
    token = os.environ.get("INEGI_TOKEN")
    if not token:
        return None
    url = (
        "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/"
        f"{INEGI_INDICATOR_INPC_YOY}/es/0700/false/BIE/2.0/{token}?type=json"
    )
    req = urllib.request.Request(url, headers={"user-agent": UA, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-mxcpi] INEGI fetch failed: {e}", file=sys.stderr)
        return None
    # INEGI JSON shape: { "Series": [ { "OBSERVATIONS": [ {"TIME_PERIOD": "...", "OBS_VALUE": "..."}, ... ] } ] }
    try:
        series = data.get("Series") or []
        if not series:
            return None
        obs = series[0].get("OBSERVATIONS") or []
    except (AttributeError, TypeError):
        print(f"[emit-mxcpi] INEGI response unexpected shape", file=sys.stderr)
        return None
    vals: list[float] = []
    for row in obs[:3]:
        try:
            vals.append(float(row.get("OBS_VALUE", "")))
        except (ValueError, TypeError):
            continue
    if len(vals) < 2:
        return None
    return sum(vals) / len(vals)


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-mxcpi] missing env: {key}", file=sys.stderr)
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


def blend(consensus: float | None, trend: float | None) -> tuple[float, float, list[str]]:
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
    if abs(delta) < 0.1:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def regime_annotation(value: float) -> str:
    if value >= 5.0:  return "hot MX inflation (Banxico hawkish pressure)"
    if value >= 4.0:  return "above Banxico target band (3% +/- 1pp)"
    if value >= 3.0:  return "upper half of Banxico band"
    if value >= 2.0:  return "lower half of Banxico band"
    return "below Banxico target / disinflation"


def format_value(v: float) -> str:
    return f"{v:+.1f}%"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-mxcpi")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None,
                    used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'-' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f}pp |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pp", unit="pp")
    return f"""# MX CPI prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** y/y MX INPC

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

`v1.1-inegi`: inverse-MAE-weighted blend of FF consensus + INEGI BIE
INPC y/y 3-mo mean trend. INEGI trend fetched from
inegi.org.mx/app/api/indicadores (indicator 628194, BIE source, last
3 observations). Trend sub-model soft-skips when INEGI_TOKEN env not
set; predictor degrades to consensus-only.

## Positioning

Phase 13 MXN expansion CPI predictor. Banxico targets 3% CPI y/y
(+/- 1pp band). Released monthly by INEGI ~2nd week of following month
at 06:00 CST (12:00 UTC winter).

## Caveats

FRED coverage for Mexico CPI is stale (CPALTT01MXM659N last obs
2025-03). INEGI is the authoritative source but requires a free
account token. Once INEGI_TOKEN is set on the farraf-cpu repo, the
trend anchor activates automatically.

## Change log

- **v1.1-inegi ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - added INEGI BIE trend anchor (opt-in via INEGI_TOKEN). Same pattern as KOSIS/MOSPI/ESTAT.
- **v1-simple-blend (2026-09-03)** - first ship. Phase 13 MXN expansion. Consensus-only pending INEGI API integration.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "MXCPI_RELEASE_DATE", "MXCPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["MXCPI_RELEASE_DATE"]
    days_out = int(os.environ["MXCPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1.1-inegi")

    consensus = parse_float("MXCPI_CONSENSUS")
    trend = fetch_inegi_trend()

    if consensus is None and trend is None:
        print("[emit-mxcpi] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("mxcpi")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-mxcpi] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-mxcpi] MXCPI {release} T-{days_out}: {format_value(point)} y/y "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")
    if trend     is not None: print(f"  trend:     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"mxcpi-{release}",
        "eventTitle": "MX INPC y/y",
        "country": "MXN",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/mxcpi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"mxcpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-mxcpi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-mxcpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
