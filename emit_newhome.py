"""New Home Sales predictor + emitter. `v1-simple-blend`.

Monthly release, ~4th week of month, 10:00 ET by Census. Value format:
annualized rate in thousands of new single-family homes sold (typical
range 600-750K). Companion to Existing Home Sales; smaller volume but
more rate-sensitive since new construction is mortgage-financed at 90%+.

Sub-models:
  - Bloomberg / FF consensus (~40K MAE on annualized rate)
  - FRED HSN1F 3-month trend (~55K MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     NEWHOME_RELEASE_DATE, NEWHOME_DAYS_OUT, NEWHOME_CONSENSUS_K, MODEL_VERSION
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
    "consensus": 40.0,
    "trend":     55.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-newhome] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_k(env_key: str) -> float | None:
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
        print(f"[emit-newhome] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_newhome_trend(api_key: str) -> float | None:
    """3-month mean of HSN1F (New 1-Family Houses Sold, SA annualized, K)."""
    obs = _fetch_fred_observations(api_key, "HSN1F", 3)
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
    if abs(delta) < 10:  # 10K = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.0f}K"
    return f"below consensus by {abs(delta):.0f}K"


def regime_annotation(value: float) -> str:
    """New home sales regime. Historical range 400-1000K annualized."""
    if value >= 750: return "hot new-home market"
    if value >= 650: return "healthy new-home market"
    if value >= 550: return "slowing new-home market"
    return "weak new-home market"


def format_value(k: float) -> str:
    """New home convention: whole thousand + K. e.g. '650K'."""
    return f"{round(k)}K"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.0f}K'} | {MAE[name]:.0f}K |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# New Home Sales prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** annualized new single-family home sales (SA)

- Regime: {regime_annotation(point)}
- 68% CI: [{round(point - sigma)}K, {round(point + sigma)}K]
- 95% CI: [{round(point - 2*sigma)}K, {round(point + 2*sigma)}K]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~40K) + FRED
HSN1F 3-month trend (~55K). New Home Sales is more rate-sensitive than
Existing — 90%+ of new-home purchases are mortgage-financed.

## Phase 2 targets

- **Mortgage rate 4-week lag** — Freddie Mac 30-yr fixed 4-week lag
  correlates ~-0.65 with new home sales (rate up → sales down after 1mo,
  faster reaction than existing)
- **NAHB Housing Market Index cross** — HMI is a builder-sentiment survey
  released ~5 days before New Home Sales; leading indicator
- **Housing Starts as trailing anchor** — Starts leads Sales by 3-6 months
  on the supply side (built homes take time to sell)

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 18th event covered.
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
            print(f"[emit-newhome] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-newhome] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "NEWHOME_RELEASE_DATE", "NEWHOME_DAYS_OUT"):
        require_env(k)

    release = os.environ["NEWHOME_RELEASE_DATE"]
    days_out = int(os.environ["NEWHOME_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_k("NEWHOME_CONSENSUS_K")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_newhome_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-newhome] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-newhome] NewHome {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.0f}K, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.0f}K")
    if trend     is not None: print(f"  trend(3mo): {trend:.0f}K")

    prediction = {
        "eventSlug": f"newhome-{release}",
        "eventTitle": "US New Home Sales",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma), round(point + sigma)],
            "ci95": [round(point - 2 * sigma), round(point + 2 * sigma)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/newhome-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"newhome-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-newhome] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-newhome] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
