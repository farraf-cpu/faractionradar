"""PCE predictor + emitter. `v1-simple-blend`.

PCE (Personal Consumption Expenditures Price Index) is the Fed's preferred
inflation gauge — released monthly ~30 days after the reference month as
part of the Personal Income and Outlays release. Headline m/m %-change
format, analogous to CPI/PPI.

Sub-models (up to 2 in v1):
  - Bloomberg / FF consensus (~0.05pp historical MAE — tightest of the
    inflation prints; analysts scrutinize PCE heavily as the Fed target)
  - FRED PCEPI 6-mo trend (~0.10pp)

No Kalshi market sub-model in v1 (PCE has less retail visibility than
CPI; Kalshi PCE contract presence unverified as of 2026-09-03 — add if it
appears in the ladder scan).

Env (set by GHA workflow):
  FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
  PCE_RELEASE_DATE, PCE_DAYS_OUT, PCE_CONSENSUS_PCT, MODEL_VERSION
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
    "cleveland_fed": 0.04,   # daily nowcast; tighter than consensus for PCE
    "trend":         0.10,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-pce] missing env: {key}", file=sys.stderr)
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
        print(f"[emit-pce] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_cleveland_fed_nowcast() -> float | None:
    """Latest non-empty 'PCE Inflation' m/m nowcast from Cleveland Fed.
    Cleveland Fed cycles between CPI + PCE nowcast windows; returns None
    when the PCE series is empty (CPI cycle currently active)."""
    url = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json"
    req = urllib.request.Request(url, headers={"user-agent": UA, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-pce] Cleveland Fed fetch failed: {e}", file=sys.stderr)
        return None
    if not isinstance(data, list) or not data:
        return None
    for ds in data[0].get("dataset") or []:
        if ds.get("seriesname") != "PCE Inflation":
            continue
        non_empty = [x for x in ds.get("data") or [] if x.get("value")]
        if not non_empty:
            return None
        try:
            return float(non_empty[-1]["value"])
        except (ValueError, TypeError):
            return None
    return None


def fetch_fred_pce_trend(api_key: str) -> float | None:
    """Mean of last 6 published m/m %-changes of PCEPI (Personal Consumption
    Expenditures Chain-type Price Index)."""
    obs = _fetch_fred_observations(api_key, "PCEPI", 8)
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
    if abs(delta) < 0.02:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def format_value(pct: float) -> str:
    return f"{pct:+.1f}%"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    cleveland_fed: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f} pp |"
        for name, v in (("consensus", consensus), ("cleveland_fed", cleveland_fed), ("trend", trend))
    )
    return f"""# PCE prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)} m/m** (PCE Price Index)

- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%]
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of consensus (0.05pp) +
Cleveland Fed daily nowcast (0.04pp; when PCE cycle active) + FRED
PCEPI 6-mo m/m trend (0.10pp). Consensus MAE on PCE is tighter than
CPI/PPI because it's the Fed's target — analysts scrutinize it more.

Phase 2 target adds Core PCE decomposition and splits headline vs
core into separate slugs (pce-<date> vs pce-core-<date>).
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
            print(f"[emit-pce] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-pce] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "PCE_RELEASE_DATE", "PCE_DAYS_OUT"):
        require_env(k)

    release = os.environ["PCE_RELEASE_DATE"]
    days_out = int(os.environ["PCE_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1.1-simple-blend")

    consensus = parse_pct("PCE_CONSENSUS_PCT")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_pce_trend(fred_key) if fred_key else None
    cleveland_fed = fetch_cleveland_fed_nowcast()

    if consensus is None and trend is None and cleveland_fed is None:
        print("[emit-pce] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, cleveland_fed, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-pce] PCE {release} T-{days_out}: {format_value(point)} m/m "
          f"(sigma {sigma:.2f}pp, used: {', '.join(used)})")
    if consensus     is not None: print(f"  consensus:      {consensus:+.2f}%")
    if cleveland_fed is not None: print(f"  cleveland_fed:  {cleveland_fed:+.2f}%")
    if trend         is not None: print(f"  trend(6mo):     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"pce-{release}",
        "eventTitle": "US PCE Price Index m/m",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/pce-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, cleveland_fed, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"pce-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-pce] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-pce] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
