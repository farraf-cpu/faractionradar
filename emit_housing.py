"""Housing Starts predictor + emitter. `v1-simple-blend`.

Monthly release ~16th-19th of month, 08:30 ET by Census. Annualized rate
of new residential construction starts (single-family + multi-family).
FF reports as `1.35M` (millions); FRED HOUST reports as thousands.

Sub-models:
  - Bloomberg / FF consensus (~40K MAE on the annualized rate)
  - FRED HOUST 3-month trend (~60K MAE — housing series is trend-persistent
    so short window works better than 6mo)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     HOUSING_RELEASE_DATE, HOUSING_DAYS_OUT, HOUSING_CONSENSUS_M, MODEL_VERSION
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

# MAE in millions of annualized starts. Consensus ~0.04M = 40K annualized.
# Trend wider because rate-sensitive series turn on mortgage-rate inflections.
MAE = {
    "consensus": 0.04,
    "trend":     0.06,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-housing] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_m(env_key: str) -> float | None:
    """Env value is a bare number in millions (e.g. '1.35'). FF format is
    '1.35M' — the workflow strips the M before passing here."""
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
        print(f"[emit-housing] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [o for o in (data.get("observations") or [])
           if o.get("value") not in (None, ".", "")]
    return obs or None


def fetch_fred_housing_trend(api_key: str) -> float | None:
    """3-month mean of HOUST (Housing Starts, SA), converted to millions.
    FRED reports HOUST in thousands of annualized starts (e.g. 1350)."""
    obs = _fetch_fred_observations(api_key, "HOUST", 3)
    if not obs or len(obs) < 3:
        return None
    vals_m = [float(o["value"]) / 1000.0 for o in obs[:3]]
    return sum(vals_m) / len(vals_m)


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
    if abs(delta) < 0.01:  # 10K annualized = noise
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta*1000:.0f}K"
    return f"below consensus by {abs(delta)*1000:.0f}K"


def regime_annotation(value: float) -> str:
    """Housing-cycle regime. Historical post-2015 range 1.0-1.8M."""
    if value >= 1.6: return "strong construction cycle"
    if value >= 1.4: return "moderate construction cycle"
    if value >= 1.2: return "slowing construction cycle"
    return "weak construction cycle"


def format_value(m: float) -> str:
    """Housing convention: 2 decimals + M suffix. e.g. '1.35M'."""
    return f"{m:.2f}M"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.2f}M'} | {MAE[name]*1000:.0f}K |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    return f"""# Housing Starts prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** annualized starts (SA)

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

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~40K MAE) + FRED
HOUST 3-month trend (~60K MAE). Housing Starts is trend-persistent so a
short 3-month trend window captures direction changes.

Phase 2 targets:
- **Building Permits leading indicator** — FRED PERMIT publishes same day
  as Starts; use as a co-anchor rather than trend-alone
- **Mortgage rate cross** — Freddie Mac 30-year fixed (FRED MORTGAGE30US)
  is the main driver of Starts turns. Add a mortgage-rate-change sub-model
  that flags direction when the 4-week average moves >25bp
- **Regional split** — Northeast/Midwest/South/West follow different
  seasonal patterns; South is ~50% of national starts
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
            print(f"[emit-housing] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-housing] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "HOUSING_RELEASE_DATE", "HOUSING_DAYS_OUT"):
        require_env(k)

    release = os.environ["HOUSING_RELEASE_DATE"]
    days_out = int(os.environ["HOUSING_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_m("HOUSING_CONSENSUS_M")
    fred_key = os.environ.get("FRED_API_KEY")
    trend = fetch_fred_housing_trend(fred_key) if fred_key else None

    if consensus is None and trend is None:
        print("[emit-housing] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, trend)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-housing] Housing {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma*1000:.0f}K, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.2f}M")
    if trend     is not None: print(f"  trend(3mo): {trend:.2f}M")

    prediction = {
        "eventSlug": f"housing-{release}",
        "eventTitle": "US Housing Starts (annualized)",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/housing-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, trend, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"housing-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-housing] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-housing] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
