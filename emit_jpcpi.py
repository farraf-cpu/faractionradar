"""JP CPI (National Core CPI y/y) predictor. v1.1-estat.

MIC (Ministry of Internal Affairs and Communications) publishes
National Core CPI y/y ~19th-27th of following month at 08:30 JST
(23:30 UTC prior day / 00:30 UTC same day depending on JST-UTC offset).

v1.1 adds e-Stat trend anchor sub-model. FRED's Japan CPI series
(JPNCPIALLMINMEI, CPALTT01JPM659N, JPNCPICORMINMEI) all discontinued
2022; e-Stat (api.e-stat.go.jp) is Japan's official statistics
portal and the only fresh source of JP CPI data.

Activate: set ESTAT_APP_ID env var to a free e-Stat API key
(register at https://www.e-stat.go.jp/api/en/). When key absent,
falls back to consensus-only (v1 behavior).

Value format: y/y %-change (e.g. "+2.9%").
Sub-models:
  - FF consensus (~0.15pp MAE)
  - e-Stat National Core CPI y/y 3-mo mean (~0.25pp MAE) [opt-in]

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     JPCPI_RELEASE_DATE, JPCPI_DAYS_OUT, JPCPI_CONSENSUS, MODEL_VERSION
     ESTAT_APP_ID (optional, activates e-Stat trend anchor)
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
    _post_to_worker(url, auth_key, payload, tag="emit-jpcpi")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 0.15,
    "trend":     0.25,   # e-Stat National Core CPI y/y 3-mo mean
}

# e-Stat National Core CPI (excluding fresh food) y/y series.
# Table 0003143513 = "Monthly CPI - by Item - Japan".
# cdCat01 = "0001" is the "総合(除く生鮮食品)" (all items less fresh food) code.
# cdCat02 = "01" is "前年同月比" (y/y % change) presentation.
ESTAT_STATS_DATA_ID = "0003143513"
ESTAT_CAT01 = "0001"
ESTAT_CAT02 = "01"


def fetch_estat_trend() -> float | None:
    """3-mo mean of JP National Core CPI y/y from e-Stat API.
    Returns None if ESTAT_APP_ID env not set or API errors.
    Requires free API key registered at https://www.e-stat.go.jp/api/en/."""
    app_id = os.environ.get("ESTAT_APP_ID")
    if not app_id:
        return None
    params = urllib.parse.urlencode({
        "appId": app_id,
        "statsDataId": ESTAT_STATS_DATA_ID,
        "cdCat01": ESTAT_CAT01,
        "cdCat02": ESTAT_CAT02,
        "limit": "3",
        "sectionHeaderFlg": "2",
    })
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?" + params
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-jpcpi] e-Stat fetch failed: {e}", file=sys.stderr)
        return None
    try:
        values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
    except (KeyError, TypeError):
        print(f"[emit-jpcpi] e-Stat response missing VALUE", file=sys.stderr)
        return None
    vals = []
    for v in values:
        try:
            vals.append(float(v.get("$", "")))
        except (ValueError, TypeError):
            continue
    if len(vals) < 2:
        return None
    return sum(vals) / len(vals)


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-jpcpi] missing env: {key}", file=sys.stderr)
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
    if value >= 3.0:  return "hot JP inflation (BOJ hawkish pressure)"
    if value >= 2.0:  return "above BOJ target"
    if value >= 1.5:  return "near BOJ target"
    if value >= 0.5:  return "below target"
    return "deflationary / disinflation"


def format_value(v: float) -> str:
    return f"{v:+.1f}%"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-jpcpi")


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
    return f"""# JP CPI prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** y/y JP National Core CPI

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

`v1.1-estat`: inverse-MAE-weighted blend of FF consensus + e-Stat
3-mo mean y/y trend. e-Stat trend fetched from api.e-stat.go.jp
(statsDataId 0003143513, cdCat01 0001 = "総合(除く生鮮食品)").
Trend sub-model soft-skips when ESTAT_APP_ID env not set;
predictor degrades to consensus-only (v1 behavior).

## Positioning

Second Phase 4 (JPY expansion) predictor. National Core CPI y/y is
BOJ's preferred inflation gauge. Released by MIC ~19th-27th of
following month at 08:30 JST.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Phase 4 JPY expansion. Consensus-only pending e-Stat API.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "JPCPI_RELEASE_DATE", "JPCPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["JPCPI_RELEASE_DATE"]
    days_out = int(os.environ["JPCPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("JPCPI_CONSENSUS")
    trend = fetch_estat_trend()

    if consensus is None and trend is None:
        print("[emit-jpcpi] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("jpcpi")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-jpcpi] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-jpcpi] JPCPI {release} T-{days_out}: {format_value(point)} y/y "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")
    if trend is not None:     print(f"  trend:     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"jpcpi-{release}",
        "eventTitle": "JP National Core CPI y/y",
        "country": "JPY",
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
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"jpcpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-jpcpi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-jpcpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
