"""Retail Sales backtest — v1 (trend only) vs v1.1 (trend + auto_leading).

Backtests the FRED-based sub-models introduced 2026-09-07:
  - v1 baseline:  RSXFS 6-mo trend
  - v1.1 add-on:  TOTALSA auto-sales leading indicator (AUTO_SHARE_COEFF = 0.22)

See backtest/README.md for scope + caveats. Consensus + Kalshi sub-models
are NOT backtested here (data unavailable).
"""
from __future__ import annotations

import os
import statistics
from datetime import date, datetime, timedelta

from harness import (
    BacktestRow,
    BacktestSummary,
    DEFAULT_CAVEATS,
    fetch_fred_history,
    format_report,
    mom_pct_from_levels,
    obs_to_floats,
    slice_at_date,
)


# Must match live predictor coefficients (emit_retail.py).
AUTO_SHARE_COEFF = 0.22


def _release_proxy_date(obs_date_str: str) -> str:
    """Given a FRED observation date (e.g. '2024-08-01' for August 2024
    data), return the approximate release date (~15th of the following
    month).
    """
    obs_dt = datetime.strptime(obs_date_str, "%Y-%m-%d").date()
    if obs_dt.month == 12:
        rel = date(obs_dt.year + 1, 1, 15)
    else:
        rel = date(obs_dt.year, obs_dt.month + 1, 15)
    return rel.isoformat()


def run(n: int = 24) -> str:
    """Run backtest over N most recent Retail Sales releases.
    Returns a markdown report."""
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# Retail backtest — FRED_API_KEY missing, aborted."

    rsxfs = fetch_fred_history(api_key, "RSXFS", limit=n + 20)
    totalsa = fetch_fred_history(api_key, "TOTALSA", limit=n + 20)
    if not rsxfs or len(rsxfs) < 10:
        return "# Retail backtest — insufficient RSXFS history."
    if not totalsa or len(totalsa) < 5:
        return ("# Retail backtest — insufficient TOTALSA history "
                "(v1.1 sub-model will be null for all rows)")

    rows: list[BacktestRow] = []
    # Iterate over the most recent N observations to treat as "targets."
    # Skip the very newest to leave room for edge cases with unfilled
    # revision windows. Use i in [1, n+1) so rsxfs[i] is the target.
    for i in range(1, min(n + 1, len(rsxfs) - 1)):
        target = rsxfs[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        # Point-in-time filter: what FRED knew before this release
        rsxfs_available = slice_at_date(rsxfs, release_date)
        if len(rsxfs_available) < 7:
            continue

        # v1: 6-month mean m/m from 7 most recent levels available
        recent_levels = obs_to_floats(rsxfs_available[:7])
        if len(recent_levels) < 7:
            continue
        v1_mom = mom_pct_from_levels(recent_levels)
        if len(v1_mom) < 6:
            continue
        v1_trend = statistics.mean(v1_mom)

        # v1.1: apply auto_leading modulation (trend + coeff * totalsa m/m)
        v1_1_pred = None
        totalsa_available = slice_at_date(totalsa, release_date)
        if len(totalsa_available) >= 2:
            ts_vals = obs_to_floats(totalsa_available[:2])
            if len(ts_vals) == 2 and ts_vals[1] > 0:
                ts_mom = (ts_vals[0] - ts_vals[1]) / ts_vals[1] * 100.0
                v1_1_pred = v1_trend + AUTO_SHARE_COEFF * ts_mom

        # Actual: m/m of the target vs the observation immediately preceding it
        # in the history (rsxfs[i+1], since rsxfs is sorted desc)
        if i + 1 >= len(rsxfs):
            continue
        try:
            target_val = float(target["value"])
            prev_val = float(rsxfs[i + 1]["value"])
        except (ValueError, KeyError):
            continue
        if prev_val <= 0:
            continue
        actual = (target_val - prev_val) / prev_val * 100.0

        rows.append(BacktestRow(
            release_date=release_date,
            v1_pred=v1_trend,
            v1_1_pred=v1_1_pred,
            actual=actual,
        ))

    # Sort ascending for readable report
    rows.sort(key=lambda r: r.release_date)

    v1_summary = BacktestSummary.from_errors(
        "v1", [r.v1_err for r in rows])
    v1_1_summary = BacktestSummary.from_errors(
        "v1.1", [r.v1_1_err for r in rows])

    return format_report(
        "US Advance Retail Sales m/m",
        rows,
        [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            "- **Retail-specific:** AUTO_SHARE_COEFF = 0.22 is the "
            "coefficient shipped in `emit_retail.py`. Backtest measures "
            "this specific value; sensitivity sweep is a follow-up.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
