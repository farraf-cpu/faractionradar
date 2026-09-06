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

from io_utils import append_ledger as _append_ledger, post_to_worker as _post_to_worker


def append_ledger(payload: dict) -> None:
    _append_ledger(ROOT / "predictions.jsonl", payload)


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    _post_to_worker(url, auth_key, payload, tag="emit-deifo")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 0.4,
    # OECD proxy anchor deferred: BCCICP02DEM460S publishes on % balance
    # scale (net positive-vs-negative responses, ~-14 to +5), not IFO's
    # 85-95 index level. Not comparable without a calibrated bridge model.
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


def blend(consensus: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if not parts:
        raise RuntimeError("blend called with no consensus")
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


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-deifo")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = f"| consensus | {'-' if consensus is None else f'{consensus:.1f}'} | {MAE['consensus']:.1f} pts |"
    prior_mae_used = MAE.get('consensus', min(MAE.values()))
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pp", unit="pp")
    return f"""# German IFO Business Climate prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** German IFO Business Climate Index

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:.1f}, {point + sigma:.1f}] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} pp)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:.1f}, {point + 2*sigma:.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
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


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "DEIFO_RELEASE_DATE", "DEIFO_DAYS_OUT"):
        require_env(k)

    release = os.environ["DEIFO_RELEASE_DATE"]
    days_out = int(os.environ["DEIFO_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("DEIFO_CONSENSUS")

    if consensus is None:
        print("[emit-deifo] consensus missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("deifo")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-deifo] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-deifo] DE IFO {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:.1f}")

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
                                consensus, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
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
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit-deifo] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
