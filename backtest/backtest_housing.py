"""Housing Starts backtest — v1 vs v1.1.

  v1:   HOUST 3-month trend (mean of last 3 levels, converted to millions).
  v1.1: inverse-MAE blend of HOUST 3-mo trend + PERMIT 3-mo trend,
        matching live emit_housing.py's blend() call. First backtest
        pass measured aux (PERMIT) alone which showed spurious
        regression; corrected here to reflect what the live predictor
        actually does.

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


# Inverse-MAE weights matching live emit_housing.py's MAE dict (both in
# millions of annualized starts):
HOUST_MAE = 0.06
PERMIT_MAE = 0.07


def _release_proxy_date(obs_date_str: str) -> str:
    """Point-in-time cutoff = target obs date (see backtest_retail.py for
    the rationale). Conservative on PERMIT: same-month PERMIT publishes
    same day as HOUST, so live v1.1 would have it. Preserves v1 vs v1.1
    direction; understates v1.1 improvement."""
    return obs_date_str


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

        # v1.1: inverse-MAE blend of HOUST trend + PERMIT trend, matching
        # live emit_housing.py behavior. Weight = 1/MAE^2 (inverse variance).
        v1_1_pred = None
        if permit:
            permit_avail = slice_at_date(permit, release_date)
            if len(permit_avail) >= 3:
                permit_vals_m = [v / 1000.0 for v in obs_to_floats(permit_avail[:3])]
                if len(permit_vals_m) == 3:
                    permit_trend = statistics.mean(permit_vals_m)
                    w_h = 1.0 / (HOUST_MAE ** 2)
                    w_p = 1.0 / (PERMIT_MAE ** 2)
                    v1_1_pred = (w_h * v1_trend + w_p * permit_trend) / (w_h + w_p)

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
            "- **Housing-specific:** v1.1 is now an inverse-MAE blend of "
            f"HOUST trend (MAE {HOUST_MAE*1000:.0f}K) + PERMIT trend "
            f"(MAE {PERMIT_MAE*1000:.0f}K), matching live emit_housing.py. "
            "First backtest pass measured PERMIT alone and produced a "
            "spurious regression; corrected to reflect actual live behavior.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
