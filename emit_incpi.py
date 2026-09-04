"""IN CPI predictor. v1.1-mospi.

MoSPI (India) publishes monthly All India CPI (Combined) y/y ~12th
of following month at 17:30 IST (12:00 UTC). RBI targets 4% CPI y/y
(2-6% tolerance band).

v1.1 adds MoSPI trend anchor sub-model via India's Open Government
Data platform (data.gov.in). FRED CPALTT01INM659N is stale;
data.gov.in is the authoritative free API for MoSPI datasets.

Activate:
1. Register free key at https://data.gov.in/user/register (~5 min)
2. Set MOSPI_APP_ID as GHA secret
3. Set MOSPI_RESOURCE_ID env var to the data.gov.in resource UUID for
   "All India Consumer Price Index Numbers" (default provided may
   need updating per data.gov.in dataset versions)

Falls back to consensus-only (v1) when key/resource missing.

Value format: y/y %-change (e.g. "+3.5%").
Sub-models:
  - FF consensus (~0.15pp MAE)
  - MoSPI (data.gov.in) 3-mo mean y/y (~0.25pp MAE) [opt-in]

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     INCPI_RELEASE_DATE, INCPI_DAYS_OUT, INCPI_CONSENSUS, MODEL_VERSION
     MOSPI_APP_ID (optional, activates MoSPI trend anchor)
     MOSPI_RESOURCE_ID (optional, overrides default CPI dataset UUID)
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

ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 0.15,
    "trend":     0.25,   # MoSPI CPI y/y 3-mo mean via data.gov.in
}

# Default data.gov.in resource UUID for "All India Consumer Price
# Index Numbers (Combined)". Data.gov.in may version datasets; user
# can override via MOSPI_RESOURCE_ID env var.
MOSPI_DEFAULT_RESOURCE_ID = "25e2ff34-45f6-49f6-a1b3-b6c4c0c72bfd"


def fetch_mospi_trend() -> float | None:
    """3-mo mean of IN CPI y/y from data.gov.in (MoSPI dataset).
    Returns None if MOSPI_APP_ID unset or API errors.
    Requires free key registered at https://data.gov.in/user/register."""
    app_id = os.environ.get("MOSPI_APP_ID")
    if not app_id:
        return None
    resource_id = os.environ.get("MOSPI_RESOURCE_ID", MOSPI_DEFAULT_RESOURCE_ID)
    params = urllib.parse.urlencode({
        "api-key": app_id,
        "format": "json",
        "limit": "12",  # last year for filtering
        "sort[Year]": "desc",
    })
    url = f"https://api.data.gov.in/resource/{resource_id}?" + params
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-incpi] MoSPI fetch failed: {e}", file=sys.stderr)
        return None
    records = data.get("records") or []
    if not records:
        print(f"[emit-incpi] MoSPI response missing records", file=sys.stderr)
        return None
    # data.gov.in CPI schemas vary. Look for numeric y/y or inflation
    # field. Common field names: "inflation", "yoy", "annual_inflation",
    # "cpi_urban_inflation", "cpi_combined_inflation", etc.
    yoy_keys = ("inflation", "yoy", "annual_inflation", "yoy_inflation",
                "cpi_combined_inflation", "cpi_general_inflation",
                "combined_inflation_rate", "index_change_percent")
    vals = []
    for row in records[:3]:
        for k in yoy_keys:
            v = row.get(k)
            if v is None:
                continue
            try:
                vals.append(float(v))
                break
            except (ValueError, TypeError):
                continue
    if len(vals) < 2:
        print(f"[emit-incpi] MoSPI records had no parseable y/y field", file=sys.stderr)
        return None
    return sum(vals) / len(vals)


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-incpi] missing env: {key}", file=sys.stderr)
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
        raise RuntimeError("blend called with no sub-models")
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


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


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None,
                    used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'-' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f}pp |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# IN CPI prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** y/y IN CPI (All India Combined)

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%]
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1.1-mospi`: inverse-MAE-weighted blend of FF consensus + MoSPI
3-mo mean y/y trend via data.gov.in API. Trend sub-model soft-skips
when MOSPI_APP_ID env not set; predictor degrades to consensus-only.

## Positioning

Second Phase 14 (INR expansion) predictor. RBI targets 4% CPI y/y
(2-6% tolerance band). Released by MoSPI ~12th of following month
at 17:30 IST.

## Caveats

FRED coverage for Japan CPI is dead — an MoSPI MoSPI Statistical Portal API integration
(mospi.gov.in, free with registration) would give a real trend
anchor. Phase 14.1 target.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Phase 14 INR expansion. Consensus-only pending MoSPI MoSPI Statistical Portal API.
"""


def append_ledger(payload: dict) -> None:
    ledger = ROOT / "predictions.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": auth_key,
            "user-agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[emit-incpi] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-incpi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "INCPI_RELEASE_DATE", "INCPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["INCPI_RELEASE_DATE"]
    days_out = int(os.environ["INCPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("INCPI_CONSENSUS")
    trend = fetch_mospi_trend()

    if consensus is None and trend is None:
        print("[emit-incpi] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-incpi] INCPI {release} T-{days_out}: {format_value(point)} y/y "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")
    if trend is not None:     print(f"  trend:     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"incpi-{release}",
        "eventTitle": "IN CPI y/y",
        "country": "INR",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/incpi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"incpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-incpi] wrote {report_path.relative_to(ROOT)}")

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
    append_ledger(ledger_row)
    print(f"[emit-incpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
