"""Empire State Manufacturing Index predictor + emitter. `v1-simple-blend`.

Monthly release, ~15th of month, 08:30 ET by Federal Reserve Bank of NY.
Value format: diffusion index level where 0 = neutral (unlike ISM's 50).
Typical range -20 to +30. First regional Fed manufacturing survey each
month — leads ISM Mfg by 2-3 weeks.

Sub-models:
  - Bloomberg / FF consensus (~4 index points MAE)
  - FRED GACDISA066MSFRBNY 3-month trend (~5 pts MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     EMPIRE_RELEASE_DATE, EMPIRE_DAYS_OUT, EMPIRE_CONSENSUS, MODEL_VERSION
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
    "consensus": 4.0,
    "trend":     5.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-empire] missing env: {key}", file=sys.stderr)
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
        print(f"[emit-empire] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_empire_trend(api_key: str) -> float | None:
    """3-month mean of GACDISA066MSFRBNY (Empire State General Business
    Conditions — Current, SA diffusion index)."""
    obs = _fetch_fred_observations(api_key, "GACDISA066MSFRBNY", 3)
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
    if abs(delta) < 1.0:  # 1 index pt = noise on Empire State
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    """Empire State regime: 0 = neutral, positive = expansion."""
    if value >= 10:  return "solid regional expansion"
    if value >= 0:   return "modest regional expansion"
    if value >= -10: return "modest regional contraction"
    return "sharp regional contraction"


def format_value(v: float) -> str:
    """Empire State convention: signed 1-decimal. e.g. '-5.3' or '+8.7'."""
    return f"{v:+.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# Empire State Manufacturing prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** Empire State General Business Conditions

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:+.1f}, {point + sigma:+.1f}]
- 95% CI: [{point - 2*sigma:+.1f}, {point + 2*sigma:+.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~4 pts) + FRED
GACDISA066MSFRBNY 3-mo trend (~5 pts). Empire State releases ~15th of
month — first regional Fed survey ahead of ISM Manufacturing on the 1st
business day of the following month.

## Positioning

Empire State is one of five regional Fed manufacturing surveys (Empire,
Philly, Dallas, Kansas City, Richmond). Weighted composite of the five
correlates ~0.85 with ISM Mfg headline. Empire is the earliest to publish
each month, so it's the leading edge of the regional composite signal.

## Phase 2 targets

- **New Orders sub-index** — Empire's New Orders leads national manufacturing
  by 1-2 months
- **Feed into ismmfg predictor** — as a leading sub-model alongside Chicago PMI

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 23rd event covered.
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
            print(f"[emit-empire] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-empire] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "EMPIRE_RELEASE_DATE", "EMPIRE_DAYS_OUT"):
        require_env(k)

    release = os.environ["EMPIRE_RELEASE_DATE"]
    days_out = int(os.environ["EMPIRE_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("EMPIRE_CONSENSUS")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_empire_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-empire] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-empire] Empire {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:+.1f}")
    if trend     is not None: print(f"  trend(3mo): {trend:+.1f}")

    prediction = {
        "eventSlug": f"empire-{release}",
        "eventTitle": "US Empire State Manufacturing Index",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/empire-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"empire-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-empire] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-empire] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
