"""NBP Policy Rate predictor. v2-outcome-distribution.

Narodowy Bank Polski Monetary Policy Report / Policy Rate decisions
(~12x/year (monthly)). Decision at 09:45
Ottawa time (13:30 UTC).

Value format: rate level (e.g. "2.25%"). Sub-models:
  - FF consensus (~0.05pp MAE)
  - FRED IRSTCI01PLM156N (OECD Immediate Rates <24h PL) current-rate
    anchor (~0.15pp MAE - tracks NBP overnight rate within ~5-10bp)

Env: FRED_API_KEY, UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     NBP_RELEASE_DATE, NBP_DAYS_OUT, NBP_CONSENSUS, MODEL_VERSION
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
    "consensus": 0.05,
    "anchor":    0.15,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-nbp] missing env: {key}", file=sys.stderr)
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
    """Current NBP Policy Rate proxy from FRED IRSTCI01PLM156N
    (OECD Immediate Rates <24h PL). Tracks NBP overnight rate within
    ~5-10bp, monthly updates. FRED INTDSRCAM193N (CA Discount Rate)
    is discontinued 2013 (Rule 27 universal)."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return None
    url = ("https://api.stlouisfed.org/fred/series/observations?"
           "series_id=IRSTCI01PLM156N&api_key=" + api_key + "&file_type=json"
           "&sort_order=desc&limit=5")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-nbp] FRED IRSTCI01PLM156N fetch failed: {e}", file=sys.stderr)
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
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


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


def normal_cdf(x: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        return 1.0 if x >= mu else 0.0
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def compute_outcome_distribution(point: float, sigma: float,
                                  anchor: float | None) -> dict:
    """v2 outcome-distribution over standard NBP 25bp rate outcomes."""
    if anchor is None:
        return {"note": "no anchor; distribution not discretized"}
    outcomes = [
        ("hike50", anchor + 0.50, "+50bp hike"),
        ("hike25", anchor + 0.25, "+25bp hike"),
        ("hold",   anchor + 0.00, "hold"),
        ("cut25",  anchor - 0.25, "-25bp cut"),
        ("cut50",  anchor - 0.50, "-50bp cut"),
        ("cut75_plus", anchor - 0.75, "-75bp or deeper"),
    ]
    dist = {}
    for i, (key, level, _) in enumerate(outcomes):
        if i == 0:
            p = 1.0 - normal_cdf(level - 0.125, point, sigma)
        elif i == len(outcomes) - 1:
            p = normal_cdf(level + 0.125, point, sigma)
        else:
            p = (normal_cdf(level + 0.125, point, sigma)
                 - normal_cdf(level - 0.125, point, sigma))
        dist[key] = round(p, 3)
    modal_key = max(dist.items(), key=lambda x: x[1])[0]
    dist["modal"] = modal_key
    return dist


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'-' if v is None else f'{v:.2f}%'} | {MAE[name]:.2f}pp |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    return f"""# NBP Policy Rate prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** NBP Policy Rate

- 68% CI: [{point - sigma:.2f}%, {point + sigma:.2f}%]
- 95% CI: [{point - 2*sigma:.2f}%, {point + 2*sigma:.2f}%]
- Lean vs anchor: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01PLM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 21 (PLN expansion) rate-decision predictor. NBP meets
~12x/year (monthly). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Phase 21 PLN expansion opens.
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
            print(f"[emit-nbp] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-nbp] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "NBP_RELEASE_DATE", "NBP_DAYS_OUT"):
        require_env(k)

    release = os.environ["NBP_RELEASE_DATE"]
    days_out = int(os.environ["NBP_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v2-outcome-distribution")

    consensus = parse_float("NBP_CONSENSUS")
    anchor = fetch_fred_anchor()

    # Rule 35: FRED IRSTCI01PLM156N may report POLONIA overnight
    # (~3.7%) which differs from NBP Reference Rate (~5-6%). Drop
    # anchor when |consensus - anchor| > 75bp.
    if consensus is not None and anchor is not None and abs(consensus - anchor) > 0.75:
        print(f"[emit-nbp] anchor {anchor:.2f}% vs consensus {consensus:.2f}% > 75bp; dropping anchor")
        anchor = None

    if consensus is None and anchor is None:
        print("[emit-nbp] all sub-models missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    lean = lean_vs_anchor(point, anchor) if anchor is not None else "no anchor (dropped: scale mismatch)"
    outcome_dist = compute_outcome_distribution(point, sigma, anchor if anchor is not None else consensus)

    print(f"[emit-nbp] NBP {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.2f}pp, {lean}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:.2f}%")
    if anchor    is not None: print(f"  anchor:    {anchor:.2f}%")
    print(f"  outcome distribution: {outcome_dist}")

    prediction = {
        "eventSlug": f"nbp-{release}",
        "eventTitle": "NBP Policy Rate",
        "country": "PLN",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/nbp-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"nbp-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-nbp] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-nbp] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
