"""Industrial Production predictor + emitter. `v1-simple-blend`.

Monthly release, ~mid-month (15th-17th), 09:15 ET by Federal Reserve.
Value format: m/m %-change of Industrial Production Index. Direct measure
of physical output — manufacturing + mining + utilities. Sensitive to
weather (utilities), auto plant cycles (manufacturing), and oil prices
(mining).

Sub-models:
  - Bloomberg / FF consensus (~0.3pp MAE)
  - FRED INDPRO 3-month trend (~0.4pp MAE)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     INDPRO_RELEASE_DATE, INDPRO_DAYS_OUT, INDPRO_CONSENSUS_PCT, MODEL_VERSION
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
    "consensus": 0.3,
    "trend":     0.4,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-indpro] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_pct(env_key: str) -> float | None:
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
        print(f"[emit-indpro] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_indpro_trend(api_key: str) -> float | None:
    """3-month mean of INDPRO m/m %-changes. FRED reports as index level;
    compute m/m %-change from last 4 levels."""
    obs = _fetch_fred_observations(api_key, "INDPRO", 4)
    if not obs or len(obs) < 4:
        return None
    levels = [float(o["value"]) for o in obs[:4]]
    mom_pcts = []
    for i in range(3):
        prev = levels[i + 1]
        curr = levels[i]
        if prev > 0:
            mom_pcts.append((curr - prev) / prev * 100.0)
    if not mom_pcts:
        return None
    return sum(mom_pcts) / len(mom_pcts)


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
    if abs(delta) < 0.05:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def format_value(pct: float) -> str:
    return f"{pct:+.1f}%"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.2f}%'} | {MAE[name]:.1f} pp |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# Industrial Production prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)} m/m** (Industrial Production Index, SA)

- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%]
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~0.3pp) + FRED
INDPRO 3-mo trend (~0.4pp). Physical output measure — direct read on
manufacturing sector activity.

## Phase 2 targets

- **Capacity Utilization companion** — TCU (Total Capacity Utilization)
  releases same day; separate slug `capacity-<date>`
- **Manufacturing sub-index** — IPMANSICS (Mfg only) strips out utilities
  weather noise; helps on stormy months
- **Auto production tracker** — auto plant shutdowns/reopens drive 30%+
  of monthly Mfg variance; Ward's Intelligence has weekly data

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 21st event covered.
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
            print(f"[emit-indpro] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-indpro] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "INDPRO_RELEASE_DATE", "INDPRO_DAYS_OUT"):
        require_env(k)

    release = os.environ["INDPRO_RELEASE_DATE"]
    days_out = int(os.environ["INDPRO_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_pct("INDPRO_CONSENSUS_PCT")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_indpro_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-indpro] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-indpro] IndPro {release} T-{days_out}: {format_value(point)} m/m "
          f"(sigma {sigma:.2f}pp, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:+.2f}%")
    if trend     is not None: print(f"  trend(3mo): {trend:+.2f}%")

    prediction = {
        "eventSlug": f"indpro-{release}",
        "eventTitle": "US Industrial Production m/m",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/indpro-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"indpro-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-indpro] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-indpro] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
