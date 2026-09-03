"""UMich Consumer Sentiment (Preliminary) predictor + emitter. `v1-simple-blend`.

Monthly release, ~mid-month (2nd Friday), 10:00 ET by University of Michigan
Survey of Consumers. Value format: index level (typical 60-100). Unlike CB
Consumer Confidence, this series IS on FRED (UMCSENT is publicly available
under license). Correlates ~0.75 with CB Confidence but releases 2-3 weeks
earlier — often a leading indicator.

Sub-models:
  - Bloomberg / FF consensus (~1.5 index points MAE)
  - FRED UMCSENT 3-month trend (~2.5 pts MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     UMICH_RELEASE_DATE, UMICH_DAYS_OUT, UMICH_CONSENSUS, MODEL_VERSION
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
    "consensus": 1.5,
    "trend":     2.5,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-umich] missing env: {key}", file=sys.stderr)
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
        print(f"[emit-umich] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_umich_trend(api_key: str) -> float | None:
    """3-month mean of UMCSENT (Michigan Consumer Sentiment, monthly)."""
    obs = _fetch_fred_observations(api_key, "UMCSENT", 3)
    if not obs or len(obs) < 3:
        return None
    vals = [float(o["value"]) for o in obs[:3]]
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
    if abs(delta) < 0.3:  # ~0.3 pts = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    """UMich sentiment regime. Historical range 50-110."""
    if value >= 90: return "strong sentiment"
    if value >= 75: return "moderate sentiment"
    if value >= 60: return "weak sentiment"
    return "recession-level sentiment"


def format_value(v: float) -> str:
    """UMich convention: 1 decimal. e.g. '72.5'."""
    return f"{v:.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# UMich Consumer Sentiment prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** index

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

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~1.5 pts MAE) +
FRED UMCSENT 3-month trend (~2.5 pts MAE). Unlike CB Consumer Confidence,
UMCSENT is freely published on FRED — enables real trend sub-model.

## Relationship to CB Consumer Confidence

Correlates ~0.75 with CB Confidence but releases 2-3 weeks earlier
(preliminary comes mid-month vs CB's last Tuesday). Often a leading
indicator for CB Confidence direction changes.

## Phase 2 targets

- **Inflation Expectations sub-index** — UMich publishes 1-year and 5-year
  inflation expectations as sub-indices. Fed watches these; separate slug
  in Phase 2
- **Preliminary vs Revised split** — Revised release comes end-of-month
  with sample doubled. Add separate slug `umich-revised-<date>`
- **Weekly sentiment cross** — Bloomberg Weekly Consumer Comfort as high-
  frequency leading input

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 19th event covered.
  Covers Preliminary only; Revised is Phase 2.
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
            print(f"[emit-umich] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-umich] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "UMICH_RELEASE_DATE", "UMICH_DAYS_OUT"):
        require_env(k)

    release = os.environ["UMICH_RELEASE_DATE"]
    days_out = int(os.environ["UMICH_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("UMICH_CONSENSUS")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_umich_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-umich] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-umich] UMich {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.1f}")
    if trend     is not None: print(f"  trend(3mo): {trend:.1f}")

    prediction = {
        "eventSlug": f"umich-{release}",
        "eventTitle": "US UMich Consumer Sentiment (Preliminary)",
        "country": "USD",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/umich-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"umich-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-umich] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-umich] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
