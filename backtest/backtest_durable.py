"""Durable Goods Orders backtest — v1 vs v1.1.

  v1:   DGORDER 3-month m/m trend.
  v1.1: v1 + NEWORDER 3-month m/m core-orders trend (independent point).

Both output m/m %-change on headline durable goods orders.
"""
from __future__ import annotations

import os
import statistics
from datetime import date, datetime

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


def _release_proxy_date(obs_date_str: str) -> str:
    """Durable Goods releases ~4th week of following month."""
    obs_dt = datetime.strptime(obs_date_str, "%Y-%m-%d").date()
    if obs_dt.month == 12:
        rel = date(obs_dt.year + 1, 1, 26)
    else:
        rel = date(obs_dt.year, obs_dt.month + 1, 26)
    return rel.isoformat()


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# Durable backtest — FRED_API_KEY missing, aborted."

    dgorder = fetch_fred_history(api_key, "DGORDER", limit=n + 20)
    neworder = fetch_fred_history(api_key, "NEWORDER", limit=n + 20)
    if not dgorder or len(dgorder) < 10:
        return "# Durable backtest — insufficient DGORDER history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(dgorder) - 5)):
        target = dgorder[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        # v1: DGORDER trend
        avail = slice_at_date(dgorder, release_date)
        if len(avail) < 4:
            continue
        levels = obs_to_floats(avail[:4])
        if len(levels) < 4:
            continue
        v1_mom = mom_pct_from_levels(levels)
        if len(v1_mom) < 3:
            continue
        v1_trend = statistics.mean(v1_mom)

        # v1.1: NEWORDER 3-mo trend as its own point estimate
        v1_1_pred = None
        if neworder:
            new_avail = slice_at_date(neworder, release_date)
            if len(new_avail) >= 4:
                new_levels = obs_to_floats(new_avail[:4])
                if len(new_levels) >= 4:
                    new_mom = mom_pct_from_levels(new_levels)
                    if len(new_mom) >= 3:
                        v1_1_pred = statistics.mean(new_mom)

        # Actual: m/m of target vs preceding
        if i + 1 >= len(dgorder):
            continue
        try:
            tv = float(target["value"])
            pv = float(dgorder[i + 1]["value"])
        except (ValueError, KeyError):
            continue
        if pv <= 0:
            continue
        actual = (tv - pv) / pv * 100.0

        rows.append(BacktestRow(
            release_date=release_date,
            v1_pred=v1_trend,
            v1_1_pred=v1_1_pred,
            actual=actual,
        ))

    rows.sort(key=lambda r: r.release_date)
    v1_summary = BacktestSummary.from_errors("v1", [r.v1_err for r in rows])
    v1_1_summary = BacktestSummary.from_errors("v1.1", [r.v1_1_err for r in rows])

    return format_report(
        "US Durable Goods Orders m/m",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            "- **Durable-specific:** headline is famously noisy (single Boeing "
            "orders swing 2pp+). v1.1 core-orders (NEWORDER) is expected to be "
            "systematically lower-variance but may not track headline direction "
            "on months where transportation dominates.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
