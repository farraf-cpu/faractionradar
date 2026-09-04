"""Core PCE predictor + emitter. `v1-simple-blend`.

Core PCE (ex food + energy) is the Fed's actual inflation focus, not
headline. Released same day/time as CPI headline (~mid-month, 08:30 ET,
BLS). FF publishes as separate event.

Value format: `+0.3%` m/m Core PCE (ex food + energy).

Sub-models:
  - Bloomberg / FF consensus (~0.08pp MAE)
  - FRED PCEPILFE 6-mo mean m/m trend (~0.15pp MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     COREPCE_RELEASE_DATE, COREPCE_DAYS_OUT, COREPCE_CONSENSUS,
     MODEL_VERSION
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
    "consensus":     0.05,
    "cleveland_fed": 0.04,   # academic benchmark on headline CPI; slightly tighter than consensus
    "trend":         0.10,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-corepce] missing env: {key}", file=sys.stderr)
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


def fetch_fred_trend() -> float | None:
    """6-mo mean of FRED PCEPILFE m/m %-change (Core PCE ex food+energy)."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return None
    url = ("https://api.stlouisfed.org/fred/series/observations?"
           f"series_id=PCEPILFE&api_key={api_key}&file_type=json"
           "&units=pch&sort_order=desc&limit=6")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-corepce] FRED fetch failed: {e}", file=sys.stderr)
        return None
    obs = data.get("observations") or []
    vals = []
    for o in obs:
        v = o.get("value")
        if v and v != ".":
            try:
                vals.append(float(v))
            except ValueError:
                pass
    if len(vals) < 3:
        return None
    return sum(vals) / len(vals)


def fetch_cleveland_fed_nowcast() -> float | None:
    """Latest non-empty 'Core PCE Inflation' m/m nowcast from Cleveland Fed.
    Cleveland Fed cycles between CPI + PCE nowcast windows; returns None
    when the CPI series is empty (PCE cycle currently active)."""
    url = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json"
    req = urllib.request.Request(url, headers={"user-agent": UA, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-corepce] Cleveland Fed fetch failed: {e}", file=sys.stderr)
        return None
    if not isinstance(data, list) or not data:
        return None
    for ds in data[0].get("dataset") or []:
        if ds.get("seriesname") != "Core PCE Inflation":
            continue
        non_empty = [x for x in ds.get("data") or [] if x.get("value")]
        if not non_empty:
            return None
        try:
            return float(non_empty[-1]["value"])
        except (ValueError, TypeError):
            return None
    return None


def blend(consensus: float | None,
          cleveland_fed: float | None,
          trend: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if cleveland_fed is not None:
        parts.append(("cleveland_fed", cleveland_fed, MAE["cleveland_fed"]))
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
    if abs(delta) < 0.05:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def regime_annotation(value: float) -> str:
    if value >= 0.4:  return "hot core inflation (Fed hawkish trigger)"
    if value >= 0.25: return "elevated core inflation"
    if value >= 0.15: return "on-target core inflation"
    return "cooling core inflation"


def format_value(v: float) -> str:
    return f"{v:+.1f}%"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    cleveland_fed: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f}pp |"
        for name, v in (("consensus", consensus), ("cleveland_fed", cleveland_fed), ("trend", trend))
    )
    return f"""# Core PCE prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** m/m Core PCE (ex food + energy)

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

`v1.1-simple-blend`: inverse-MAE-weighted mean of FF consensus +
Cleveland Fed daily nowcast (when CPI cycle active) + FRED PCEPILFE
6-month m/m trend.

## Positioning

Core PCE (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core PCE strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** — first ship.
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
            print(f"[emit-corepce] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-corepce] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "COREPCE_RELEASE_DATE", "COREPCE_DAYS_OUT"):
        require_env(k)

    release = os.environ["COREPCE_RELEASE_DATE"]
    days_out = int(os.environ["COREPCE_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1.1-simple-blend")

    consensus = parse_float("COREPCE_CONSENSUS")
    cleveland_fed = fetch_cleveland_fed_nowcast()
    trend = fetch_fred_trend()

    if consensus is None and cleveland_fed is None and trend is None:
        print("[emit-corepce] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, cleveland_fed, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-corepce] Core PCE {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus     is not None: print(f"  consensus:      {consensus:+.2f}%")
    if cleveland_fed is not None: print(f"  cleveland_fed:  {cleveland_fed:+.2f}%")
    if trend         is not None: print(f"  trend:          {trend:+.2f}%")

    prediction = {
        "eventSlug": f"corepce-{release}",
        "eventTitle": "US Core PCE m/m",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/corepce-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, cleveland_fed, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"corepce-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-corepce] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-corepce] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
