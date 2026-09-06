"""Shared helpers for the empirical-MAE + sigma-auto-tune pattern.

Each emit_*.py predictor fetches its own MAE stats from the worker,
renders a compact accuracy section on the .md report, and (once N>=5)
swaps the inverse-MAE-derived sigma for the observed value.

Kept dependency-free (stdlib only) so any predictor can import.

Public API:
- fetch_empirical_mae(slug_prefix, tag) -> dict | None
- build_empirical_mae_section(obs, prior_mae_str, first_release_hint, unit) -> str
- auto_tune_sigma(prior, obs, threshold=5) -> (sigma, source, prior_sigma)
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
DEFAULT_THRESHOLD = 5


def fetch_empirical_mae(slug_prefix: str, tag: str = "emit") -> dict | None:
    """Read the worker's /public/models endpoint and return the empirical
    MAE + hit-rate for the given slug_prefix. Returns None on any failure
    so callers degrade to prior-MAE-only reporting.

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
        print(f"[{tag}] empirical MAE fetch failed: {e}", file=sys.stderr)
        return None
    for m in data.get("models") or []:
        if m.get("slug_prefix") == slug_prefix:
            obs = m.get("mae_observed") or {}
            if isinstance(obs, dict):
                return obs
    return None


def build_empirical_mae_section(
    obs: dict | None,
    prior_mae_str: str,
    first_release_hint: str = "first resolution pending",
    unit: str = "pp",
    threshold: int = DEFAULT_THRESHOLD,
) -> str:
    """Compact markdown section for the .md report. Empty string when
    obs is missing so callers can concat safely.

    `unit` — display suffix for the empirical MAE value ("pp" for CPI/
    FOMC/most rate + inflation, "K" for jobs-count predictors like NFP).
    """
    if not obs or not isinstance(obs, dict):
        return ""
    count = obs.get("count", 0)
    mae = obs.get("mae")
    hit_rate = obs.get("hit_rate")
    if count == 0:
        return f"""

## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | {prior_mae_str} |
| Resolved predictions | 0 ({first_release_hint}) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= {threshold} the CI sigma will switch from the prior to the
empirical value.

"""
    hits = obs.get("hits", 0)
    empirical_mae_str = (
        f"{mae:.3f} {unit}" if unit == "pp" and isinstance(mae, (int, float))
        else f"{mae:.1f} {unit}" if isinstance(mae, (int, float))
        else "—"
    )
    hit_pct = f"{hit_rate*100:.0f}%" if isinstance(hit_rate, (int, float)) else "—"
    # Trailing blank line matters — markdown tables merge with the next
    # header if no gap separates them. Bit us on 2026-09-06 smoke.
    return f"""

## Empirical accuracy (live, from resolved predictions)

| Metric | Value |
|--------|-------|
| Prior MAE claim | {prior_mae_str} |
| Resolved predictions | {count} |
| Empirical MAE | {empirical_mae_str} |
| Hit rate (ourCall closest) | {hit_pct} ({hits}/{count}) |

"""


import json
import math


def parse_market_ladder_env(env_var: str, tag: str = "emit") -> list[tuple[float, float]] | None:
    """Parse a JSON list of {threshold, probability} rungs from an env var
    (FOMC_MARKET_LADDER, CPI_MARKET_LADDER, NFP_MARKET_LADDER). Returns
    sorted (threshold_asc) tuples with valid probabilities in [0, 1], or
    None if unset/malformed/under 2 rungs."""
    raw = os.environ.get(env_var)
    if not raw:
        return None
    try:
        arr = json.loads(raw)
    except Exception as e:
        print(f"[{tag}] {env_var} parse failed: {e}", file=sys.stderr)
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
    """P(actual > x) via step-below function over discrete ladder rungs.
    Rungs are sorted (threshold_asc, P(actual >= threshold)). At x below
    the lowest rung, returns the highest probability (P >= lowest); at or
    above the top rung, returns 0."""
    for t, p in rungs:
        if x < t:
            return p
    return 0.0


def _normal_cdf(x: float, mu: float, sigma: float) -> float:
    if sigma <= 0:
        return 1.0 if x >= mu else 0.0
    return 0.5 * (1.0 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def compute_rate_outcome_distribution(
    point: float,
    sigma: float,
    anchor: float | None,
    bucket_bp: int = 25,
) -> dict:
    """Discretize N(point, sigma^2) posterior over 6 rate-decision buckets
    centered on `anchor` (current policy rate). Bucket width = bucket_bp/100.
    Return {'note': ...} when anchor is missing.

    Bucket size variants (per Rule 36 tuning):
    - 25bp default: DM central banks (ECB, BOE, BOJ, most G10 + EMs)
    - 50bp: high-cadence movers (BCB Selic — Rule 26)
    - 100bp: high-volatility EMs (CBRT — Rule 26)
    """
    if anchor is None:
        return {"note": "no anchor; distribution not discretized"}
    step = bucket_bp / 100.0
    half = step / 2.0
    outcomes = [
        ("hike50",     anchor + 2 * step),
        ("hike25",     anchor + 1 * step),
        ("hold",       anchor + 0 * step),
        ("cut25",      anchor - 1 * step),
        ("cut50",      anchor - 2 * step),
        ("cut75_plus", anchor - 3 * step),
    ]
    dist: dict = {}
    for i, (key, level) in enumerate(outcomes):
        if i == 0:
            p = 1.0 - _normal_cdf(level - half, point, sigma)
        elif i == len(outcomes) - 1:
            p = _normal_cdf(level + half, point, sigma)
        else:
            p = (_normal_cdf(level + half, point, sigma)
                 - _normal_cdf(level - half, point, sigma))
        dist[key] = round(p, 3)
    modal_key = max(dist.items(), key=lambda x: x[1])[0]
    dist["modal"] = modal_key
    return dist


RATE_OUTCOME_LABELS = {
    "hike50": "+50bp hike",
    "hike25": "+25bp hike",
    "hold":   "hold",
    "cut25":  "-25bp cut",
    "cut50":  "-50bp cut",
    "cut75_plus": "-75bp or deeper",
}
_RATE_OUTCOME_ORDER = ["hike50", "hike25", "hold", "cut25", "cut50", "cut75_plus"]


def build_rate_outcome_dist_table(dist: dict | None) -> str:
    """Compact markdown section for a rate-decision outcome distribution.
    Returns empty string when the distribution is missing so callers can
    concatenate unconditionally. Shared by every rate-decision emitter
    (fomc has its own copy that predates this helper)."""
    if not dist or not isinstance(dist, dict):
        return ""
    modal = dist.get("modal")
    src = dist.get("source", "unknown")
    rows: list[str] = []
    for k in _RATE_OUTCOME_ORDER:
        v = dist.get(k)
        if not isinstance(v, (int, float)):
            continue
        marker = " **(modal)**" if k == modal else ""
        rows.append(f"| {RATE_OUTCOME_LABELS.get(k, k)} | {v*100:.1f}%{marker} |")
    if not rows:
        return ""
    body = "\n".join(rows)
    return f"""

## Outcome distribution (source: `{src}`)

| Outcome | Probability |
|---------|-------------|
{body}

"""


def auto_tune_sigma(
    prior_sigma: float,
    obs: dict | None,
    threshold: int = DEFAULT_THRESHOLD,
) -> tuple[float, str]:
    """Return (effective_sigma, source_label). If obs has count>=threshold
    and a positive numeric MAE, swap prior_sigma for the empirical value.
    Otherwise keep the prior."""
    if obs and isinstance(obs.get("count"), int) and obs["count"] >= threshold:
        emp = obs.get("mae")
        if isinstance(emp, (int, float)) and emp > 0:
            return float(emp), f"empirical (n={obs['count']})"
    return prior_sigma, "prior (inverse-MAE)"
