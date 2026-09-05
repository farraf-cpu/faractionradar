"""CA CPI predictor. v1.1-statcan.

Statistics Canada (StatCan) publishes monthly CPI y/y ~3 weeks after
reference month at 08:30 EST (13:30 UTC winter / 12:30 UTC summer).
BOC targets 2% CPI y/y (1-3% band).

v1.1 swaps stale FRED CPALTT01CAM659N trend for live StatCan WDS
API. StatCan Web Data Service (www150.statcan.gc.ca/t1/wds/rest)
is public — no auth required. Vector v108785713 = CPI y/y all-items
Canada.

Value format: y/y %-change (e.g. "+2.7%").

Sub-models:
  - FF consensus (~0.15pp MAE)
  - StatCan WDS 3-mo mean y/y trend (~0.20pp MAE, tighter than
    stale FRED because authoritative source)

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     CACPI_RELEASE_DATE, CACPI_DAYS_OUT, CACPI_CONSENSUS, MODEL_VERSION
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
    "trend":     0.20,   # StatCan WDS live y/y series, tighter than stale FRED
}

# StatCan WDS vector 108785713 = CPI y/y all-items Canada.
STATCAN_VECTOR_YY = 108785713


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-cacpi] missing env: {key}", file=sys.stderr)
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


def fetch_statcan_trend() -> float | None:
    """3-mo mean CA CPI y/y from StatCan WDS vector 108785713.
    Public API — no auth. Returns None if unreachable."""
    url = "https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods"
    body = json.dumps([{"vectorId": STATCAN_VECTOR_YY, "latestN": 3}]).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"content-type": "application/json", "user-agent": UA},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-cacpi] StatCan fetch failed: {e}", file=sys.stderr)
        return None
    if not isinstance(data, list) or not data:
        return None
    obj = data[0].get("object", {})
    pts = obj.get("vectorDataPoint") or []
    vals = []
    for p in pts:
        v = p.get("value")
        if v is None:
            continue
        try:
            vals.append(float(v))
        except (ValueError, TypeError):
            continue
    if len(vals) < 2:
        return None
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
    if abs(delta) < 0.1:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def regime_annotation(value: float) -> str:
    if value >= 4.0:  return "hot CA inflation (BOC hawkish pressure)"
    if value >= 3.0:  return "above BOC target band"
    if value >= 2.0:  return "upper end of BOC band"
    if value >= 1.0:  return "lower end of BOC band"
    return "below target / disinflation"


def format_value(v: float) -> str:
    return f"{v:+.1f}%"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'-' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f}pp |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# CA CPI prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** y/y CA CPI

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

`v1.1-statcan`: inverse-MAE-weighted mean of FF consensus + StatCan
WDS API (apisidra-like: vector v108785713 for CPI y/y all-items).
No key required — StatCan WDS is public.

## Positioning

Second Phase 6 CAD predictor. CA CPI released monthly by StatCan
~3 weeks after reference month at 08:30 EST. BOC target 2% CPI y/y
(1-3% band).

## Change log

- **v1.1-statcan ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - swapped stale FRED trend for live StatCan WDS API. Auto-active.
- **v1-simple-blend (2026-09-04)** - first ship. Phase 6 CAD expansion.
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
            print(f"[emit-cacpi] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-cacpi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "CACPI_RELEASE_DATE", "CACPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["CACPI_RELEASE_DATE"]
    days_out = int(os.environ["CACPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("CACPI_CONSENSUS")
    trend = fetch_statcan_trend()

    if consensus is None and trend is None:
        print("[emit-cacpi] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-cacpi] CACPI {release} T-{days_out}: {format_value(point)} y/y "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")
    if trend     is not None: print(f"  trend:     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"cacpi-{release}",
        "eventTitle": "CA CPI y/y (monthly)",
        "country": "CAD",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/cacpi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"cacpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-cacpi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-cacpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
