"""JOLTS Job Openings predictor + emitter. `v1-simple-blend`.

Monthly release, ~1st week of month, 10:00 ET by BLS. Value format: level
of job openings in millions (e.g. `7.20M`). Labor-market slack indicator —
Fed watches openings/unemployed ratio closely.

Sub-models:
  - Bloomberg / FF consensus (~150K openings MAE)
  - FRED JTSJOL 3-month trend (~250K MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     JOLTS_RELEASE_DATE, JOLTS_DAYS_OUT, JOLTS_CONSENSUS_M, MODEL_VERSION
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

# MAE in millions of openings.
MAE = {
    "consensus": 0.15,
    "trend":     0.25,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-jolts] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_m(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={urllib.parse.quote(series_id)}"
           f"&api_key={urllib.parse.quote(api_key)}"
           f"&file_type=json&sort_order=desc&limit={limit}")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-jolts] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_jolts_trend(api_key: str) -> float | None:
    """3-month mean of JTSJOL (Job Openings level, SA) converted to millions.
    FRED reports as thousands."""
    obs = _fetch_fred_observations(api_key, "JTSJOL", 3)
    if not obs or len(obs) < 3:
        return None
    vals = [float(o["value"]) / 1000.0 for o in obs[:3]]
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
    if abs(delta) < 0.05:  # 50K = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta*1000:.0f}K"
    return f"below consensus by {abs(delta)*1000:.0f}K"


def regime_annotation(value: float) -> str:
    """JOLTS regime label. Post-2022 range 7-11M, pre-COVID 5.5-7.5M."""
    if value >= 9.0: return "extremely tight labor demand"
    if value >= 8.0: return "tight labor demand"
    if value >= 7.0: return "moderating labor demand"
    return "softening labor demand"


def format_value(m: float) -> str:
    """JOLTS convention: 2 decimals + M suffix. e.g. '7.20M'."""
    return f"{m:.2f}M"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.2f}M'} | {MAE[name]*1000:.0f}K |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# JOLTS Job Openings prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** job openings (level, SA)

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:.2f}M, {point + sigma:.2f}M]
- 95% CI: [{point - 2*sigma:.2f}M, {point + 2*sigma:.2f}M]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~150K MAE) +
FRED JTSJOL 3-month trend (~250K MAE). Short trend window because JOLTS
has been volatile since 2022 (multiple months of 500K+ revisions).

## Why the Fed watches this

Openings/Unemployed ratio (JOLTS Job Openings / U-3 unemployment level) is
Fed Chair Powell's preferred labor-tightness gauge. Ratio >1.5 = extremely
tight; ratio ~1.0 = balanced; ratio <0.8 = slack. Our regime labels use
the openings level directly since the ratio requires waiting for NFP too.

Phase 2 target:
- **Openings/Unemployed ratio** — cross-fetch NFP unemployment level from
  KV, publish ratio alongside headline as a Fed-decision-relevant metric
- **Quits Rate sub-model** — JTSQUL (Quits Level) leads Openings by ~1
  month; add as sub-model
- **Hires vs Separations gap** — JTSHIL - JTSTSL is net employment
  addition; add as sanity check on Openings trend
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
            print(f"[emit-jolts] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-jolts] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "JOLTS_RELEASE_DATE", "JOLTS_DAYS_OUT"):
        require_env(k)

    release = os.environ["JOLTS_RELEASE_DATE"]
    days_out = int(os.environ["JOLTS_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_m("JOLTS_CONSENSUS_M")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_jolts_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-jolts] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-jolts] JOLTS {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma*1000:.0f}K, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.2f}M")
    if trend     is not None: print(f"  trend(3mo): {trend:.2f}M")

    prediction = {
        "eventSlug": f"jolts-{release}",
        "eventTitle": "US JOLTS Job Openings",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/jolts-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"jolts-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-jolts] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-jolts] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
