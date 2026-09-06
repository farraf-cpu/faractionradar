"""FOMC predictor + emitter. v1-simple-blend: publishes an implied
federal funds target rate as a point estimate (not a discrete outcome
distribution — that's Phase 2). Prediction markets dominate the blend
because they've historically led rate-decision calls.

Env (set by GHA workflow):
  UPLOAD_AUTH_KEY       — POST auth to /upload
  CALENDAR_WORKER_URL   — https://faractionradar-calendar.faractionradar.workers.dev
  FOMC_RELEASE_DATE     — YYYY-MM-DD
  FOMC_DAYS_OUT         — 7|4|3|2|1
  FOMC_MARKET_RATE      — Kalshi-implied rate (parsed by workflow from /public/kalshi-implied fomc.value_k)
  FRED_API_KEY          — optional; used for current fed funds target fallback
  MODEL_VERSION         — default "v1-simple-blend"

Note: consensus for FOMC is often blank in FF (rare release with no forecast
column), so we rely on markets + current-rate anchor. Consensus is wired
optionally via FOMC_CONSENSUS_RATE for later expansion.
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

# Historical MAE benchmarks (percentage points on target rate).
# Market: Kalshi/fed-funds-futures typically ~5bp (0.05pp) on rate-decision
# days. Consensus: analysts often stop publishing FF forecasts entirely,
# but when they do, ~7bp. Anchor (current rate) is a no-change assumption
# with wide error — only used as fallback so we don't return zero.
MAE = {
    "market":    0.05,
    "consensus": 0.07,
    "anchor":    0.25,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-fomc] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_rate(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def fetch_current_fed_funds(api_key: str) -> float | None:
    """DFEDTARU (upper bound of target range) — most recent observation.
    Returns rate as a percent (e.g. 4.25 for 4.25%)."""
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id=DFEDTARU&api_key={urllib.parse.quote(api_key)}"
           "&file_type=json&sort_order=desc&limit=1")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-fomc] FRED DFEDTARU fetch failed: {e}", file=sys.stderr)
        return None
    obs = data.get("observations") or []
    if not obs:
        return None
    v = obs[0].get("value")
    if v in (None, ".", ""):
        return None
    try:
        return float(v)
    except ValueError:
        return None


def blend(market: float | None,
          consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if market is not None:
        parts.append(("market", market, MAE["market"]))
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


def format_rate(pct: float) -> str:
    """FOMC convention: two decimals, e.g. '4.25%'."""
    return f"{pct:.2f}%"


def normal_cdf(x: float, mu: float, sigma: float) -> float:
    """Cumulative distribution function of normal distribution. Pure Python
    (no scipy dep needed) using math.erf."""
    if sigma <= 0:
        return 1.0 if x >= mu else 0.0
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def fetch_empirical_mae(slug_prefix: str) -> dict | None:
    """Read the worker's /public/models endpoint and return the empirical
    MAE + hit-rate for our slug_prefix. Returns None on any failure so
    callers degrade to prior-MAE-only reporting.

    Shape: {"count": int, "mae": float|None, "hits": int, "hit_rate": float|None}
    """
    base = os.environ.get("CALENDAR_WORKER_URL", "").rstrip("/")
    if not base:
        return None
    url = f"{base}/public/models"
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[emit-fomc] empirical MAE fetch failed: {e}", file=sys.stderr)
        return None
    for m in data.get("models") or []:
        if m.get("slug_prefix") == slug_prefix:
            obs = m.get("mae_observed") or {}
            if isinstance(obs, dict):
                return obs
    return None


def parse_market_ladder() -> list[tuple[float, float]] | None:
    """FOMC_MARKET_LADDER = JSON list of {threshold, probability} rungs
    representing P(target_rate > threshold) from Kalshi's FED-DECISION
    series. Returns sorted (threshold_asc) tuples, or None if unset or
    malformed."""
    raw = os.environ.get("FOMC_MARKET_LADDER")
    if not raw:
        return None
    try:
        arr = json.loads(raw)
    except Exception as e:
        print(f"[emit-fomc] FOMC_MARKET_LADDER parse failed: {e}", file=sys.stderr)
        return None
    rungs: list[tuple[float, float]] = []
    for r in arr if isinstance(arr, list) else []:
        try:
            t = float(r["threshold"])
            p = float(r["probability"])
        except (KeyError, TypeError, ValueError):
            continue
        if 0.0 <= p <= 1.0:
            rungs.append((t, p))
    if len(rungs) < 2:
        return None
    rungs.sort(key=lambda x: x[0])
    return rungs


def survival_from_ladder(x: float, rungs: list[tuple[float, float]]) -> float:
    """P(rate > x) under the discrete-support assumption that all mass lives
    at Fed target rungs (25bp grid). Step-below function: for r_i <= x < r_{i+1}
    the survival at x = P(rate >= r_{i+1}) = rungs[i+1].p. Below the lowest
    rung we return the highest probability (P >= lowest_rung); at or above
    the top rung we return 0 (assume no tail above the top contract)."""
    for t, p in rungs:
        if x < t:
            return p
    return 0.0


def compute_outcome_distribution(point: float, sigma: float,
                                  anchor: float | None,
                                  ladder: list[tuple[float, float]] | None = None
                                  ) -> dict:
    """v2 upgrade: discretize into probabilities over standard FOMC
    outcomes at 25bp intervals around the current rate.

    v2.1 (ladder mode): when a Kalshi ladder is available, derive
    per-bucket probs directly from market survival P(rate > x) by
    differencing adjacent bucket edges. This replaces the normal-CDF
    approximation and lets the market's actual per-outcome pricing
    drive the distribution.

    Buckets (relative to current anchor rate):
      hike50: current + 0.50%
      hike25: current + 0.25%
      hold:   current + 0.00%
      cut25:  current - 0.25%
      cut50:  current - 0.50%
      cut75+: current - 0.75% and below
    """
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

    dist: dict = {}
    if ladder is not None:
        # Kalshi ladder path: per-bucket = P(rate > lower_edge) - P(rate > upper_edge).
        # Tail buckets extend one edge to +/- infinity (clamped by survival_from_ladder).
        for i, (key, level, _) in enumerate(outcomes):
            if i == 0:
                p = survival_from_ladder(level - 0.125, ladder)
            elif i == len(outcomes) - 1:
                p = 1.0 - survival_from_ladder(level + 0.125, ladder)
            else:
                p = (survival_from_ladder(level - 0.125, ladder)
                     - survival_from_ladder(level + 0.125, ladder))
            dist[key] = round(max(0.0, min(1.0, p)), 3)
        # Renormalize in case interpolation nudged the sum off 1.0 by a bit.
        total = sum(dist[k] for k, _, _ in outcomes)
        if total > 0:
            for key, _, _ in outcomes:
                dist[key] = round(dist[key] / total, 3)
        dist["source"] = "kalshi-ladder"
    else:
        for i, (key, level, _) in enumerate(outcomes):
            if i == 0:
                p = 1.0 - normal_cdf(level - 0.125, point, sigma)
            elif i == len(outcomes) - 1:
                p = normal_cdf(level + 0.125, point, sigma)
            else:
                p = (normal_cdf(level + 0.125, point, sigma)
                     - normal_cdf(level - 0.125, point, sigma))
            dist[key] = round(p, 3)
        dist["source"] = "gaussian-approx"

    modal_key = max(
        ((k, dist[k]) for k, _, _ in outcomes),
        key=lambda x: x[1],
    )[0]
    dist["modal"] = modal_key
    return dist


def lean_vs_current(point: float, anchor: float | None) -> str:
    if anchor is None:
        return "no current-rate anchor available"
    delta_bp = round((point - anchor) * 100)
    if abs(delta_bp) < 5:
        return "hold expected (in line with current target)"
    if delta_bp <= -25:
        return f"cut of ~{abs(delta_bp)}bp expected"
    if delta_bp >= 25:
        return f"hike of ~{delta_bp}bp expected"
    return f"{delta_bp:+d}bp move vs current expected"


def build_empirical_mae_section(obs: dict | None, prior_mae_str: str) -> str:
    """Show empirical accuracy alongside the prior MAE claim. Renders
    a compact table so readers can compare 'what we said our MAE would
    be' vs 'what it actually is on resolved predictions'."""
    if not obs or not isinstance(obs, dict):
        return ""
    count = obs.get("count", 0)
    mae = obs.get("mae")
    hit_rate = obs.get("hit_rate")
    if count == 0:
        # Pre-resolution: still show the section so readers see the promise
        # of transparency even when N=0.
        return f"""

## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | {prior_mae_str} |
| Resolved predictions | 0 (first FOMC print pending) |
| Empirical MAE | — |
| Hit rate vs consensus | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the inverse-MAE-derived prior
to the empirical value.
"""
    hits = obs.get("hits", 0)
    empirical_mae_str = f"{mae:.3f} pp" if isinstance(mae, (int, float)) else "—"
    hit_pct = f"{hit_rate*100:.0f}%" if isinstance(hit_rate, (int, float)) else "—"
    return f"""

## Empirical accuracy (live, from resolved predictions)

| Metric | Value |
|--------|-------|
| Prior MAE claim | {prior_mae_str} |
| Resolved predictions | {count} |
| Empirical MAE | {empirical_mae_str} |
| Hit rate vs consensus | {hit_pct} ({hits}/{count}) |
"""


def build_outcome_dist_table(dist: dict | None) -> str:
    """Render the outcome distribution as a compact markdown table.
    Returns empty string when the distribution is missing so callers
    can concatenate unconditionally."""
    if not dist:
        return ""
    labels = {
        "hike50": "+50bp hike",
        "hike25": "+25bp hike",
        "hold":   "hold",
        "cut25":  "-25bp cut",
        "cut50":  "-50bp cut",
        "cut75_plus": "-75bp or deeper",
    }
    order = ["hike50", "hike25", "hold", "cut25", "cut50", "cut75_plus"]
    modal = dist.get("modal")
    src = dist.get("source", "unknown")
    rows = []
    for k in order:
        v = dist.get(k)
        if not isinstance(v, (int, float)):
            continue
        marker = " **(modal)**" if k == modal else ""
        rows.append(f"| {labels[k]} | {v*100:.1f}%{marker} |")
    if not rows:
        return ""
    body = "\n".join(rows)
    return f"""

## Outcome distribution (source: `{src}`)

| Outcome | Probability |
|---------|-------------|
{body}
"""


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, market: float | None,
                    consensus: float | None, anchor: float | None,
                    used: list[str], lean: str,
                    outcome_dist: dict | None = None,
                    empirical_mae: dict | None = None,
                    sigma_source: str = "prior (inverse-MAE)",
                    prior_sigma: float | None = None) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else format_rate(v)} | {MAE[name]:.2f} pp |"
        for name, v in (("market", market), ("consensus", consensus), ("anchor", anchor))
    )
    dist_section = build_outcome_dist_table(outcome_dist)
    # Prior MAE claim = the tightest sub-model MAE currently in the blend
    # (market at 0.05pp when Kalshi is available, else consensus 0.07pp).
    prior_mae_used = min(MAE[u] for u in used if u in MAE) if used else min(MAE.values())
    empirical_section = build_empirical_mae_section(empirical_mae, f"{prior_mae_used:.2f} pp")
    return f"""# FOMC prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_rate(point)}** target fed funds rate

- 68% CI: [{point - sigma:.2f}%, {point + sigma:.2f}%] · sigma source: {sigma_source}{f" (prior was {prior_sigma:.2f}pp)" if prior_sigma is not None and sigma_source.startswith("empirical") else ""}
- 95% CI: [{point - 2*sigma:.2f}%, {point + 2*sigma:.2f}%]
- Direction: {lean}
- Sub-models used: {', '.join(used)}
{dist_section}{empirical_section}
## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

v2.1-kalshi-ladder: point estimate is an inverse-MAE-weighted mean of
market + consensus + anchor sub-models. The outcome distribution over
hike50 / hike25 / hold / cut25 / cut50 / cut75+ is derived directly from
the Kalshi FED-DECISION contract ladder when available (source =
kalshi-ladder), falling back to a normal-CDF approximation of the point
+ sigma when no ladder is present (source = gaussian-approx).

Ladder path: each bucket prob = P(rate > lower_edge) - P(rate > upper_edge)
via a step-below survival function over discrete ladder rungs, then
renormalized to sum 1. This gives the market's actual per-outcome pricing
instead of assuming Gaussian residuals — meaningful for rate-cut skew events.
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
            print(f"[emit-fomc] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-fomc] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "FOMC_RELEASE_DATE", "FOMC_DAYS_OUT"):
        require_env(k)

    release = os.environ["FOMC_RELEASE_DATE"]
    days_out = int(os.environ["FOMC_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    market = parse_rate("FOMC_MARKET_RATE")
    consensus = parse_rate("FOMC_CONSENSUS_RATE")
    fred_key = os.environ.get("FRED_API_KEY")
    anchor = fetch_current_fed_funds(fred_key) if fred_key else None

    if market is None and consensus is None and anchor is None:
        print("[emit-fomc] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(market, consensus, anchor)
    prior_sigma = sigma
    lean = lean_vs_current(point, anchor)
    ladder = parse_market_ladder()
    outcome_dist = compute_outcome_distribution(point, sigma, anchor, ladder=ladder)

    # Empirical MAE auto-tune: same pattern as emit_cpi. When >=5 resolved
    # FOMC predictions exist, swap prior sigma for observed MAE so the CI
    # reflects real accuracy. Below threshold we keep the prior.
    empirical_mae = fetch_empirical_mae("fomc")
    sigma_source = "prior (inverse-MAE)"
    if empirical_mae and isinstance(empirical_mae.get("count"), int) and empirical_mae["count"] >= 5:
        emp_val = empirical_mae.get("mae")
        if isinstance(emp_val, (int, float)) and emp_val > 0:
            sigma = float(emp_val)
            sigma_source = f"empirical (n={empirical_mae['count']})"
            print(f"[emit-fomc] sigma auto-tuned: prior={prior_sigma:.3f}pp -> empirical={sigma:.3f}pp (n={empirical_mae['count']})")

    print(f"[emit-fomc] FOMC {release} T-{days_out}: {format_rate(point)} "
          f"(sigma {sigma:.3f}pp, used: {', '.join(used)})")
    if market    is not None: print(f"  market:     {market:.2f}%")
    if consensus is not None: print(f"  consensus:  {consensus:.2f}%")
    if anchor    is not None: print(f"  anchor:     {anchor:.2f}%")
    print(f"  outcome distribution: {outcome_dist}")

    prediction = {
        "eventSlug": f"fomc-{release}",
        "eventTitle": "FOMC federal funds rate decision",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_rate(point),
            "lean": lean,
            "ci68": [round(point - sigma, 2), round(point + sigma, 2)],
            "ci95": [round(point - 2 * sigma, 2), round(point + 2 * sigma, 2)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
            "outcomeDistribution": outcome_dist,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/fomc-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                market, consensus, anchor, used, lean,
                                outcome_dist=outcome_dist,
                                empirical_mae=empirical_mae,
                                sigma_source=sigma_source,
                                prior_sigma=prior_sigma)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"fomc-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-fomc] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-fomc] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
