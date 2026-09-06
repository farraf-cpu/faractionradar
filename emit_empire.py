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

from fred_utils import fetch_fred_observations as _fetch_fred_observations_raw


def _fetch_fred_observations(api_key: str, series_id: str, limit: int) -> list[dict] | None:
    return _fetch_fred_observations_raw(api_key, series_id, limit, tag="emit-empire")


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


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-empire")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    trend: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("trend", trend))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pts", unit="pts")
    return f"""# Empire State Manufacturing prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** Empire State General Business Conditions

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:+.1f}, {point + sigma:+.1f}] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} pts)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:+.1f}, {point + 2*sigma:+.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}
{empirical_section}
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
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("empire")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-empire] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
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
                                consensus, trend, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
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
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit-empire] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
