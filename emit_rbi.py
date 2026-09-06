"""RBI Policy Rate predictor. v2-outcome-distribution.

Reserve Bank of India Monetary Policy Report / Policy Rate decisions
(~8x/year). Decision at 09:45
Ottawa time (04:30 UTC).

Value format: rate level (e.g. "2.25%"). Sub-models:
  - FF consensus (~0.05pp MAE)
  - FRED IRSTCI01INM156N (OECD Immediate Rates <24h IN) current-rate
    anchor (~0.15pp MAE - tracks RBI overnight rate within ~5-10bp)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     RBI_RELEASE_DATE, RBI_DAYS_OUT, RBI_CONSENSUS, MODEL_VERSION
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
    _post_to_worker(url, auth_key, payload, tag="emit-rbi")


ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

MAE = {
    "consensus": 0.05,
    "anchor":    1.00,   # FRED IRSTCI01INM156N is close to policy rate actual RBI repo rate; heavily deweighted
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-rbi] missing env: {key}", file=sys.stderr)
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


def fetch_fred_anchor() -> float | None:
    """Current RBI Policy Rate proxy from FRED IRSTCI01INM156N
    (OECD Immediate Rates <24h IN). Tracks RBI overnight rate within
    ~5-10bp, monthly updates. FRED INTDSRCAM193N (CA Discount Rate)
    is discontinued 2013 (Rule 27 universal)."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return None
    url = ("https://api.stlouisfed.org/fred/series/observations?"
           "series_id=IRSTCI01INM156N&api_key=" + api_key + "&file_type=json"
           "&sort_order=desc&limit=5")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-rbi] FRED IRSTCI01INM156N fetch failed: {e}", file=sys.stderr)
        return None
    obs = data.get("observations") or []
    for o in obs:
        v = o.get("value")
        if v and v != ".":
            try:
                return float(v)
            except ValueError:
                pass
    return None


def blend(consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if anchor is not None:
        parts.append(("anchor", anchor, MAE["anchor"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    return inverse_variance_combine(parts)


def lean_vs_anchor(point: float, anchor: float | None) -> str:
    if anchor is None:
        return "no anchor"
    delta = point - anchor
    if abs(delta) < 0.02:
        return "hold expected"
    bp = round(delta * 100)
    if bp > 0:
        return f"+{bp}bp move vs current rate"
    return f"{bp}bp cut vs current rate"


def format_value(v: float) -> str:
    return f"{v:.2f}%"


from mae_utils import fetch_empirical_mae as _fetch_empirical_mae, build_empirical_mae_section, auto_tune_sigma, build_rate_outcome_dist_table, compute_rate_outcome_distribution, inverse_variance_combine


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    return _fetch_empirical_mae(slug_prefix, tag="emit-rbi")


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None,
                    outcome_dist: dict | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'-' if v is None else f'{v:.2f}%'} | {MAE[name]:.2f}pp |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pp", unit="pp")
    dist_section = build_rate_outcome_dist_table(outcome_dist)
    return f"""# RBI Policy Rate prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** RBI Policy Rate

- 68% CI: [{point - sigma:.2f}%, {point + sigma:.2f}%] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f} pp)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:.2f}%, {point + 2*sigma:.2f}%]
- Lean vs anchor: {lean}
- Sub-models used: {', '.join(used)}
{dist_section}{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01INM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 14 (INR expansion) rate-decision predictor. RBI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Phase 14 INR expansion opens.
"""


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "RBI_RELEASE_DATE", "RBI_DAYS_OUT"):
        require_env(k)

    release = os.environ["RBI_RELEASE_DATE"]
    days_out = int(os.environ["RBI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v2-outcome-distribution")

    consensus = parse_float("RBI_CONSENSUS")
    anchor = fetch_fred_anchor()

    # Guard: FRED IRSTCI01INM156N runs ~close to policy rate actual Banxico
    # target rate. If consensus and anchor differ by >75bp, drop anchor
    # to avoid scale-mismatch cascading into wrong outcome distribution.
    if consensus is not None and anchor is not None and abs(consensus - anchor) > 0.75:
        print(f"[emit-rbi] anchor {anchor:.2f}% vs consensus {consensus:.2f}% > 75bp; dropping anchor")
        anchor = None

    if consensus is None and anchor is None:
        print("[emit-rbi] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    prior_sigma = sigma
    empirical_mae = fetch_empirical_mae("rbi")
    sigma, sigma_source = auto_tune_sigma(prior_sigma, empirical_mae)
    if sigma_source.startswith("empirical"):
        print(f"[emit-rbi] sigma auto-tuned: prior={prior_sigma:.3f} -> empirical={sigma:.3f}")
    lean = lean_vs_anchor(point, anchor) if anchor is not None else "no anchor (dropped: scale mismatch)"
    outcome_dist = compute_outcome_distribution(point, sigma, anchor if anchor is not None else consensus)

    print(f"[emit-rbi] RBI {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.2f}pp, {lean}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:.2f}%")
    if anchor    is not None: print(f"  anchor:    {anchor:.2f}%")
    print(f"  outcome distribution: {outcome_dist}")

    prediction = {
        "eventSlug": f"rbi-{release}",
        "eventTitle": "RBI Policy Rate",
        "country": "INR",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma, 2), round(point + sigma, 2)],
            "ci95": [round(point - 2 * sigma, 2), round(point + 2 * sigma, 2)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
            "outcomeDistribution": outcome_dist,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/rbi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma,
                                outcome_dist=outcome_dist)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"rbi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-rbi] wrote {report_path.relative_to(ROOT)}")

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
    if isinstance(outcome_dist, dict):
        modal = outcome_dist.get("modal")
        source = outcome_dist.get("source")
        if modal:
            ledger_row["modalOutcome"] = modal
        if source:
            ledger_row["outcomeSource"] = source
    if sigma_source.startswith("empirical"):
        ledger_row["sigmaSource"] = sigma_source
    append_ledger(ledger_row)
    print(f"[emit-rbi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
