"""CPI predictor + emitter. Simpler than NFP — v1-simple-blend combines
live consensus, Kalshi implied m/m, and a naive 6-month FRED trend into
an inverse-MAE weighted point estimate.

No ML sub-models yet (Phase 2 target). Ship as `v1-simple-blend` so it's
clearly labelled as first-cut and can be upgraded without breaking the
worker's schema.

Env (set by GHA workflow):
  FRED_API_KEY          — used for CPIAUCSL 6mo trend
  UPLOAD_AUTH_KEY       — POST auth to /upload
  CALENDAR_WORKER_URL   — https://faractionradar-calendar.faractionradar.workers.dev
  CPI_RELEASE_DATE      — YYYY-MM-DD of the target print
  CPI_DAYS_OUT          — 7|4|3|2|1
  CPI_CONSENSUS_PCT     — parsed by workflow from worker's FF forecast
  CPI_MARKET_PCT        — parsed by workflow from /public/kalshi-implied cpi.value_k
  MODEL_VERSION         — pinned string, default "v1-simple-blend"

Emits:
  reports/YYYY-MM/cpi-t-<N>.md
  predictions.jsonl append
  POST /upload payload matching CalendarEvent.prediction schema
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

# Historical MAE benchmarks used as inverse-variance weights in the blend.
# Consensus: Bloomberg/FF composite is ~0.08 pp on CPI m/m (industry-reported).
# Market: Kalshi CPI event MAE hard to bound before we have live scoring; use
# 0.12 pp as a conservative starting weight. Trend: naive 6-mo mean of recent
# CPI m/m as a persistence check, MAE ~0.15 pp (regime-dependent).
# Historical MAE benchmarks (percentage points on headline CPI m/m).
# Consensus: Bloomberg/FF ~0.08. Market: Kalshi ~0.12 (bootstrap). Trend: naive
# 6-mo mean of past CPIAUCSL m/m ~0.15 (regime-dependent). Trimmed-mean:
# Dallas Fed 8% trimmed-mean CPI m/m — good mean-reverting anchor, published
# alongside headline release with modest lag, historical MAE ~0.10pp when
# used as a standalone predictor of headline m/m.
MAE = {
    "consensus":     0.08,
    "cleveland_fed": 0.06,   # daily nowcast; academic benchmark, tightest sub-model
    "market":        0.12,
    "trimmed_mean":  0.10,
    "trend":         0.15,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-cpi] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_pct(env_key: str) -> float | None:
    """Env comes in as bare number (e.g. '0.2' meaning 0.2 pp)."""
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    """Shared FRED series-observations fetcher. Returns raw observations
    list (newest-first) or None on error / empty. Filters out '.' / '' values."""
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={urllib.parse.quote(series_id)}"
           f"&api_key={urllib.parse.quote(api_key)}"
           f"&file_type=json&sort_order=desc&limit={limit}")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-cpi] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_cpi_trend(api_key: str) -> float | None:
    """Return mean of last 6 published m/m %-changes of CPIAUCSL headline.
    Used only as a naive persistence-anchor sub-model."""
    obs = _fetch_fred_observations(api_key, "CPIAUCSL", 8)
    if not obs or len(obs) < 7:
        return None
    # Newest first; compute 6 most-recent m/m %-changes from 7 most-recent levels.
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


def fetch_cleveland_fed_nowcast() -> float | None:
    """Latest non-empty 'CPI Inflation' m/m nowcast from Cleveland Fed.
    Cleveland Fed cycles between CPI + PCE nowcast windows; returns None
    when the CPI series is empty (PCE cycle currently active). Sub-model
    auto-activates ~T-14 days before each CPI release."""
    url = "https://www.clevelandfed.org/-/media/files/webcharts/inflationnowcasting/nowcast_month.json"
    req = urllib.request.Request(url, headers={"user-agent": UA, "accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-cpi] Cleveland Fed fetch failed: {e}", file=sys.stderr)
        return None
    if not isinstance(data, list) or not data:
        return None
    for ds in data[0].get("dataset") or []:
        if ds.get("seriesname") != "CPI Inflation":
            continue
        non_empty = [x for x in ds.get("data") or [] if x.get("value")]
        if not non_empty:
            return None
        try:
            return float(non_empty[-1]["value"])
        except (ValueError, TypeError):
            return None
    return None


def fetch_fred_trimmed_mean(api_key: str) -> float | None:
    """Dallas Fed 8% trimmed-mean CPI m/m %-change, most recent observation.
    Series ID: TRMMEANCPIM159SFRBDAL. Published monthly alongside CPI headline;
    a good mean-reverting anchor because it excludes the top + bottom 8% of
    price change tails (energy spikes, one-off jumps). Used as a Phase 2
    sub-model that historically forecasts headline m/m with ~0.10pp MAE."""
    obs = _fetch_fred_observations(api_key, "TRMMEANCPIM159SFRBDAL", 1)
    if not obs:
        return None
    try:
        return float(obs[0]["value"])
    except (ValueError, KeyError):
        return None


def blend(consensus: float | None,
          cleveland_fed: float | None,
          market: float | None,
          trimmed_mean: float | None,
          trend: float | None) -> tuple[float, float, list[str]]:
    """Inverse-variance blend of available sub-models.
    Returns (point_estimate, blended_sigma_pp, used_labels)."""
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if cleveland_fed is not None:
        parts.append(("cleveland_fed", cleveland_fed, MAE["cleveland_fed"]))
    if market is not None:
        parts.append(("market", market, MAE["market"]))
    if trimmed_mean is not None:
        parts.append(("trimmed_mean", trimmed_mean, MAE["trimmed_mean"]))
    if trend is not None:
        parts.append(("trend", trend, MAE["trend"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")

    # weights ∝ 1/MAE (proxy for 1/σ² under normal-ish error). Not exact but
    # aligned with the NFP methodology so readers get a consistent story.
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    # Blended sigma ~ sqrt(sum(w²·MAE²))/sum(w) — inverse-variance combining
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
    """CPI convention: one decimal, signed. e.g. '+0.2%' or '-0.1%'."""
    return f"{pct:+.1f}%"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    cleveland_fed: float | None,
                    market: float | None, trimmed_mean: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.2f}%'} | {MAE[name]:.2f} pp |"
        for name, v in (("consensus", consensus), ("cleveland_fed", cleveland_fed),
                        ("market", market),
                        ("trimmed_mean", trimmed_mean), ("trend", trend))
    )
    return f"""# CPI prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)} m/m**

- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%]
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 4 sub-models.
Consensus + Kalshi market + FRED trimmed-mean CPI + FRED CPIAUCSL 6-mo
trend. Weights are `1 / MAE`, so tighter historical sources dominate.
CI is inverse-variance-combined sigma. `TRMMEANCPIM159SFRBDAL` (Dallas
Fed 8% trimmed mean m/m) added in v1.1 as a mean-reverting anchor that
excludes the top + bottom 8% of price change tails — historically
forecasts headline m/m with ~0.10pp MAE.

Phase 2 target adds Cleveland Fed nowcast + shelter/energy carve-outs
and restructures as a proper Bayesian blend with regime-aware weights.
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
            print(f"[emit-cpi] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-cpi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "CPI_RELEASE_DATE", "CPI_DAYS_OUT"):
        require_env(k)

    release = os.environ["CPI_RELEASE_DATE"]
    days_out = int(os.environ["CPI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1.1-simple-blend")

    consensus = parse_pct("CPI_CONSENSUS_PCT")
    market = parse_pct("CPI_MARKET_PCT")

    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_cpi_trend(fred_key) if fred_key else None
    trimmed_mean = fetch_fred_trimmed_mean(fred_key) if fred_key else None
    cleveland_fed = fetch_cleveland_fed_nowcast()

    if consensus is None and market is None and trend is None and trimmed_mean is None and cleveland_fed is None:
        print("[emit-cpi] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, cleveland_fed, market, trimmed_mean, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-cpi] CPI {release} T-{days_out}: {format_value(point)} m/m "
          f"(sigma {sigma:.2f}pp, used: {', '.join(used)})")
    if consensus     is not None: print(f"  consensus:      {consensus:+.2f}%")
    if cleveland_fed is not None: print(f"  cleveland_fed:  {cleveland_fed:+.2f}%")
    if market        is not None: print(f"  market:         {market:+.2f}%")
    if trimmed_mean  is not None: print(f"  trimmed_mean:   {trimmed_mean:+.2f}%")
    if trend         is not None: print(f"  trend(6mo):     {trend:+.2f}%")

    prediction = {
        "eventSlug": f"cpi-{release}",
        "eventTitle": "US Consumer Price Index m/m",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/cpi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, cleveland_fed, market, trimmed_mean, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"cpi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-cpi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-cpi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
