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

from io_utils import append_ledger as _append_ledger, post_to_worker as _post_to_worker


def append_ledger(payload: dict) -> None:
    _append_ledger(ROOT / "predictions.jsonl", payload)


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    _post_to_worker(url, auth_key, payload, tag="emit-pce")


from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-pce")


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
    return inverse_variance_combine(parts)


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


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-pce")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    cleveland_fed: float | None,
                    trend: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f} pp |"
        for name, v in (("consensus", consensus), ("cleveland_fed", cleveland_fed), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pp")
    return f"""# PCE prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)} m/m** (PCE Price Index)

- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f}pp)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
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
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("pce")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-pce] sigma auto-tuned: prior={prior_sigma:.3f}pp -> empirical={sigma:.3f}pp")
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
                                consensus, cleveland_fed, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
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
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit-pce] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
