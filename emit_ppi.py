"""PPI predictor + emitter. `v1-simple-blend`.

PPI (Producer Price Index, headline m/m Final Demand) is analogous to CPI —
monthly release, %-change target. Simpler model than CPI for v1 because
Kalshi doesn't have PPI event contracts (checked 2026-09-03) and no
trimmed-mean equivalent is published on FRED for Final Demand PPI.

Sub-models (up to 2):
  - Bloomberg / FF consensus (~0.10pp historical MAE on headline m/m)
  - FRED PPIFIS 6-mo trend (~0.15pp, mean of past 6 m/m %-changes)

Env (set by GHA workflow):
  FRED_API_KEY          — for PPIFIS 6-mo trend
  UPLOAD_AUTH_KEY       — POST auth to /upload
  CALENDAR_WORKER_URL   — https://faractionradar-calendar.faractionradar.workers.dev
  PPI_RELEASE_DATE      — YYYY-MM-DD
  PPI_DAYS_OUT          — 7|4|3|2|1
  PPI_CONSENSUS_PCT     — parsed from FF forecast field
  MODEL_VERSION         — default "v1-simple-blend"

Ship pattern mirrors emit_cpi.py — same helpers, same shape, same soft-skip.
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
    "consensus": 0.10,
    "trend":     0.15,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-ppi] missing env: {key}", file=sys.stderr)
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
        print(f"[emit-ppi] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_ppi_trend(api_key: str) -> float | None:
    """Mean of last 6 published m/m %-changes of PPIFIS (Producer Price Index
    by Industry: Final Demand, SA). Persistence-anchor sub-model."""
    obs = _fetch_fred_observations(api_key, "PPIFIS", 8)
    if not obs or len(obs) < 7:
        return None
    levels = [float(o["value"]) for o in obs[:7]]
    mom_pcts = []
    for i in range(6):
        prev = levels[i + 1]
        curr = levels[i]
        if prev > 0:
            mom_pcts.append((curr - prev) / prev * 100.0)
    if not mom_pcts:
        return None
    return sum(mom_pcts) / len(mom_pcts)


def blend(consensus: float | None,
          trend: float | None) -> tuple[float, float, list[str]]:
    """Inverse-MAE-weighted blend. Returns (point, sigma, used_labels)."""
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
    if abs(delta) < 0.02:
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
        f"| {name} | {'—' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f} pp |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# PPI prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)} m/m** (Producer Price Index, Final Demand)

- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%]
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of up to 2 sub-models. Consensus
(0.10pp historical MAE) + FRED PPIFIS 6-mo m/m trend (0.15pp). Blended sigma
is the inverse-variance combination.

PPI has no Kalshi contract market (as of 2026-09-03) so no prediction-market
sub-model — this makes v1 simpler than CPI. Phase 2 target adds a
sector-decomposition sub-model (energy / food / trade services) since PPI
is more sector-heterogeneous than CPI headline.
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
            print(f"[emit-ppi] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-ppi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "PPI_RELEASE_DATE", "PPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["PPI_RELEASE_DATE"]
    days_out = int(os.environ["PPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_pct("PPI_CONSENSUS_PCT")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_ppi_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-ppi] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-ppi] PPI {release} T-{days_out}: {format_value(point)} m/m "
          f"(sigma {sigma:.2f}pp, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:+.2f}%")
    if trend     is not None: print(f"  trend(6mo): {trend:+.2f}%")

    prediction = {
        "eventSlug": f"ppi-{release}",
        "eventTitle": "US Producer Price Index m/m",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/ppi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"ppi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-ppi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-ppi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
