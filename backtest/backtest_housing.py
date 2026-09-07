"""Housing Starts backtest — v1 vs v1.1.

  v1:   HOUST 3-month trend (mean of last 3 levels, converted to millions).
  v1.1: v1 + PERMIT 3-month trend (permits leading indicator).

Values in millions of annualized starts (e.g. 1.35M). Both HOUST and PERMIT
are reported in thousands annualized on FRED — convert by /1000.
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
    obs_to_floats,
    slice_at_date,
)


def _release_proxy_date(obs_date_str: str) -> str:
    """Housing Starts release ~16-19th of the following month."""
    obs_dt = datetime.strptime(obs_date_str, "%Y-%m-%d").date()
    if obs_dt.month == 12:
        rel = date(obs_dt.year + 1, 1, 17)
    else:
        rel = date(obs_dt.year, obs_dt.month + 1, 17)
    return rel.isoformat()


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# Housing backtest — FRED_API_KEY missing, aborted."

    houst = fetch_fred_history(api_key, "HOUST", limit=n + 20)
    permit = fetch_fred_history(api_key, "PERMIT", limit=n + 20)
    if not houst or len(houst) < 5:
        return "# Housing backtest — insufficient HOUST history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(houst) - 3)):
        target = houst[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        avail = slice_at_date(houst, release_date)
        if len(avail) < 3:
            continue
        vals_m = [v / 1000.0 for v in obs_to_floats(avail[:3])]
        if len(vals_m) < 3:
            continue
        v1_trend = statistics.mean(vals_m)

        # v1.1: PERMIT 3-mo trend (independent point estimate, same units)
        v1_1_pred = None
        if permit:
            permit_avail = slice_at_date(permit, release_date)
            if len(permit_avail) >= 3:
                permit_vals_m = [v / 1000.0 for v in obs_to_floats(permit_avail[:3])]
                if len(permit_vals_m) == 3:
                    v1_1_pred = statistics.mean(permit_vals_m)

        # Actual: HOUST level for target month, in millions
        try:
            actual = float(target["value"]) / 1000.0
        except (ValueError, KeyError):
            continue

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
        "US Housing Starts (annualized)",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            "- **Housing-specific:** v1.1 sub-model is PERMIT 3-mo trend "
            "as its own point estimate (not a modulation of HOUST trend). "
            "Permits typically run slightly higher than starts (some don't "
            "convert), which introduces a documented bias.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
