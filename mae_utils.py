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
    return f"""

## Empirical accuracy (live, from resolved predictions)

| Metric | Value |
|--------|-------|
| Prior MAE claim | {prior_mae_str} |
| Resolved predictions | {count} |
| Empirical MAE | {empirical_mae_str} |
| Hit rate (ourCall closest) | {hit_pct} ({hits}/{count}) |
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
