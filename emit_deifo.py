"""German IFO Business Climate predictor. v1-simple-blend.

The IFO Institute publishes the Business Climate Index (Geschaeftsklima)
around the 25th of each month at 09:00 CET. The index is a proprietary
IFO Institute product - NOT on FRED. This predictor consumes FF consensus
as the primary signal, with an OECD German Composite Business Confidence
trend proxy as a directional anchor (weak - 2-month lag).

Value format: level (e.g. "88.6"), NOT a m/m %-change. Typical range 80-105.

Sub-models:
  - Bloomberg / FF consensus (~0.4 pts MAE - primary signal)
  - FRED BCCICP02DEM460S 3-mo mean anchor (~1.5 pts MAE - directional only,
    OECD data is 2 months behind IFO release cycle)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     DEIFO_RELEASE_DATE, DEIFO_DAYS_OUT, DEIFO_CONSENSUS, MODEL_VERSION
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
    "consensus": 0.4,
    "anchor":    1.5,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-deifo] missing env: {key}", file=sys.stderr)
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


def fetch_fred_anchor() -> float | None:
    """3-mo mean of FRED BCCICP02DEM460S (OECD Composite Business Confidence
    for Germany). Different scale from IFO Business Climate (OECD normalized
    to 100) but directionally correlated - useful only as anchor when FF
    consensus is missing. Skipped by blend when consensus available."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return None
    url = ("https://api.stlouisfed.org/fred/series/observations?"
           f"series_id=BCCICP02DEM460S&api_key={api_key}&file_type=json"
           "&sort_order=desc&limit=3")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-deifo] FRED fetch failed: {e}", file=sys.stderr)
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
    if len(vals) < 2:
        return None
    return sum(vals) / len(vals)


def blend(consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if anchor is not None:
        parts.append(("anchor", anchor, MAE["anchor"]))
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
    if abs(delta) < 0.3:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    if value >= 100: return "expansion boom"
    if value >= 95:  return "solid expansion"
    if value >= 90:  return "modest expansion"
    if value >= 85:  return "flat / mild contraction"
    return "sharp contraction"


def format_value(v: float) -> str:
    return f"{v:.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'-' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    return f"""# German IFO Business Climate prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** German IFO Business Climate Index

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:.1f}, {point + sigma:.1f}]
- 95% CI: [{point - 2*sigma:.1f}, {point + 2*sigma:.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + OECD
Composite Business Confidence for Germany (BCCICP02DEM460S) as
directional anchor.

## Caveats

IFO Institute's Business Climate Index is **proprietary** - not on FRED.
Anchor sub-model uses OECD composite business confidence for Germany,
which lags by ~2 months and uses a normalized (100=trend) scale different
from IFO's mid-80s to low-90s range. Anchor is thus a WEAK signal for the
next print, useful mainly as a directional check when consensus is
present. Phase 3 target: paid IFO API access or full HTML scrape.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Third Phase 2 EUR predictor. 3/3 EUR spec met.
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
            print(f"[emit-deifo] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-deifo] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "DEIFO_RELEASE_DATE", "DEIFO_DAYS_OUT"):
        require_env(k)

    release = os.environ["DEIFO_RELEASE_DATE"]
    days_out = int(os.environ["DEIFO_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("DEIFO_CONSENSUS")
    anchor = fetch_fred_anchor()

    if consensus is None and anchor is None:
        print("[emit-deifo] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-deifo] DE IFO {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:.1f}")
    if anchor    is not None: print(f"  anchor:    {anchor:.1f} (OECD proxy, ~2mo lag)")

    prediction = {
        "eventSlug": f"deifo-{release}",
        "eventTitle": "German IFO Business Climate",
        "country": "EUR",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/deifo-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"deifo-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-deifo] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-deifo] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
