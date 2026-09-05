"""BR CPI (IPCA) predictor. v1.1-sidra.

IBGE publishes monthly IPCA ~9-11th of following month at 09:00 BRT
(12:00 UTC). BCB targets 3% CPI y/y (+/- 1.5pp).

v1.1 adds IBGE SIDRA API trend anchor. SIDRA (apisidra.ibge.gov.br)
is IBGE's public data API — **no auth required, no key needed**.
Trend sub-model activates unconditionally.

Value format: y/y %-change (e.g. "+4.4%").
Sub-models:
  - FF consensus (~0.15pp MAE)
  - SIDRA IPCA 12-mo y/y 3-mo mean (~0.20pp MAE) [always active]

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     BRCPI_RELEASE_DATE, BRCPI_DAYS_OUT, BRCPI_CONSENSUS, MODEL_VERSION
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
    "trend":     0.20,   # SIDRA IPCA 12-mo y/y 3-mo mean
}

# IBGE SIDRA table 1737 = IPCA (Consumer Price Index).
# Variable 2265 = "Variação acumulada em 12 meses" (12-mo rolling y/y).
# Nivel 1 = Brasil (nationwide). Public API, no auth.
SIDRA_TABLE = "1737"
SIDRA_VAR_YY = "2265"


def fetch_sidra_trend() -> float | None:
    """3-mo mean of BR IPCA 12-mo y/y from SIDRA API.
    No auth required. Returns None if API errors."""
    url = (f"https://apisidra.ibge.gov.br/values/t/{SIDRA_TABLE}"
           f"/n1/all/v/{SIDRA_VAR_YY}/p/last%203/d/v{SIDRA_VAR_YY}%202")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-brcpi] SIDRA fetch failed: {e}", file=sys.stderr)
        return None
    # SIDRA returns list with first element as header row, rest data
    if not isinstance(data, list) or len(data) < 2:
        return None
    vals = []
    for row in data[1:]:
        v = row.get("V")
        if v is None or v == "-" or v == "...":
            continue
        try:
            vals.append(float(v))
        except (ValueError, TypeError):
            continue
    if len(vals) < 2:
        return None
    return sum(vals) / len(vals)


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-brcpi] missing env: {key}", file=sys.stderr)
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
    return f"""# BR CPI (IPCA) prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** y/y IPCA (12-mo rolling)

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

`v1.1-sidra`: inverse-MAE-weighted blend of FF consensus + SIDRA
IPCA 12-mo y/y 3-mo mean trend. SIDRA (apisidra.ibge.gov.br) is
IBGE's public API — no authentication required, activates
unconditionally when the API is reachable.

## Positioning

Second Phase 15 (BRL expansion) predictor. BCB targets 3% IPCA
y/y (+/- 1.5pp). Released by IBGE ~9-11th of following month at
09:00 BRT.

## Caveats

FRED coverage for Japan CPI is dead — an IBGE IBGE Statistical Portal API integration
(ibge.gov.br, free with registration) would give a real trend
anchor. Phase 15.1 target.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Phase 15 BRL expansion. Consensus-only pending IBGE IBGE Statistical Portal API.
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
            print(f"[emit-brcpi] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-brcpi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "BRCPI_RELEASE_DATE", "BRCPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["BRCPI_RELEASE_DATE"]
    days_out = int(os.environ["BRCPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("BRCPI_CONSENSUS")
    trend = fetch_sidra_trend()

    if consensus is None and trend is None:
        print("[emit-brcpi] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-brcpi] BRCPI {release} T-{days_out}: {format_value(point)} y/y "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")
    if trend is not None:     print(f"  trend:     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"brcpi-{release}",
        "eventTitle": "BR IPCA y/y",
        "country": "BRL",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/brcpi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"brcpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-brcpi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-brcpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
