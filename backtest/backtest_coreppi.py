"""Core PPI backtest — v1 vs v1.1.

  v1:   PPIFES 6-month m/m trend.
  v1.1: inverse-MAE blend of PPIFES trend + PPICMM trend, matching live
        emit_coreppi.py's blend() call. First backtest pass measured
        PPICMM alone which showed spurious regression. Even after this
        correction, OLS refit shows blend weight w=0.998 on v1 (i.e.
        PPICMM adds essentially no signal); the live v1.1 was reverted
        for this reason.

Both output m/m %-change on Core PPI (ex food + energy).
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


# Inverse-MAE weights matching live emit_coreppi.py (all in pp):
PPIFES_MAE = 0.15
PPICMM_MAE = 0.18


def _release_proxy_date(obs_date_str: str) -> str:
    """Point-in-time cutoff = target obs date (see backtest_retail.py for
    the rationale). PPIFES + PPICMM publish same day, so same-month
    conservatism matches live behavior."""
    return obs_date_str


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# Core PPI backtest — FRED_API_KEY missing, aborted."

    ppifes = fetch_fred_history(api_key, "PPIFES", limit=n + 20)
    ppicmm = fetch_fred_history(api_key, "PPICMM", limit=n + 20)
    if not ppifes or len(ppifes) < 10:
        return "# Core PPI backtest — insufficient PPIFES history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(ppifes) - 8)):
        target = ppifes[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        # v1: 6-month mean of m/m %-changes derived from levels
        avail = slice_at_date(ppifes, release_date)
        if len(avail) < 7:
            continue
        levels = obs_to_floats(avail[:7])
        if len(levels) < 7:
            continue
        v1_mom = mom_pct_from_levels(levels)
        if len(v1_mom) < 6:
            continue
        v1_trend = statistics.mean(v1_mom)

        # v1.1: inverse-MAE blend of PPIFES trend + PPICMM trend, matching
        # live emit_coreppi.py behavior.
        v1_1_pred = None
        if ppicmm:
            cmm_avail = slice_at_date(ppicmm, release_date)
            if len(cmm_avail) >= 7:
                cmm_levels = obs_to_floats(cmm_avail[:7])
                if len(cmm_levels) >= 7:
                    cmm_mom = mom_pct_from_levels(cmm_levels)
                    if len(cmm_mom) >= 6:
                        cmm_trend = statistics.mean(cmm_mom)
                        w_pf = 1.0 / (PPIFES_MAE ** 2)
                        w_pc = 1.0 / (PPICMM_MAE ** 2)
                        v1_1_pred = (w_pf * v1_trend + w_pc * cmm_trend) / (w_pf + w_pc)

        # Actual: m/m of target vs preceding
        if i + 1 >= len(ppifes):
            continue
        try:
            tv = float(target["value"])
            pv = float(ppifes[i + 1]["value"])
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
        "US Core PPI m/m",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            "- **Core PPI-specific:** v1.1 sub-model PPICMM is intermediate-"
            "materials m/m, not Core PPI. When they diverge (e.g. oil shocks "
            "transmitting to core with lag), backtest catches that.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
