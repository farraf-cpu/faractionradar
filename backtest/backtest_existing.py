"""Existing Home Sales backtest — v1 vs v1.1.

  v1:   EXHOSLUSM495S 3-month trend (annualized rate, thousands / 1000 for M).
  v1.1: v1 * (1 + MORTGAGE_SENSITIVITY * MORTGAGE30US_2mo_change_bp).

MORTGAGE30US is weekly on FRED. 2-month window ~= 9 weekly obs.
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

MORTGAGE_SENSITIVITY = -0.005  # match emit_existing.py


def _release_proxy_date(obs_date_str: str) -> str:
    """Existing Home Sales releases ~20-24th of following month."""
    obs_dt = datetime.strptime(obs_date_str, "%Y-%m-%d").date()
    if obs_dt.month == 12:
        rel = date(obs_dt.year + 1, 1, 22)
    else:
        rel = date(obs_dt.year, obs_dt.month + 1, 22)
    return rel.isoformat()


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# Existing backtest — FRED_API_KEY missing, aborted."

    existing = fetch_fred_history(api_key, "EXHOSLUSM495S", limit=n + 20)
    # MORTGAGE30US is weekly — pull ~2 years worth
    mortgage = fetch_fred_history(api_key, "MORTGAGE30US", limit=120)
    if not existing or len(existing) < 5:
        return "# Existing backtest — insufficient EXHOSLUSM495S history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(existing) - 3)):
        target = existing[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        # v1: 3-mo mean of existing home sales, in M
        avail = slice_at_date(existing, release_date)
        if len(avail) < 3:
            continue
        vals_m = [v / 1000.0 for v in obs_to_floats(avail[:3])]
        if len(vals_m) < 3:
            continue
        v1_trend = statistics.mean(vals_m)

        # v1.1: mortgage-rate 2-mo shock modulation
        v1_1_pred = None
        if mortgage:
            m_avail = slice_at_date(mortgage, release_date)
            if len(m_avail) >= 9:
                rates = obs_to_floats(m_avail[:9])
                if len(rates) >= 9:
                    recent = (rates[0] + rates[1]) / 2.0
                    lagged = (rates[7] + rates[8]) / 2.0
                    rate_change_bp = (recent - lagged) * 100.0
                    v1_1_pred = v1_trend * (1.0 + MORTGAGE_SENSITIVITY * rate_change_bp)

        # Actual: existing home sales level for target month, in M
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
        "US Existing Home Sales (annualized)",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            f"- **Existing-specific:** MORTGAGE_SENSITIVITY = "
            f"{MORTGAGE_SENSITIVITY}/bp is the pre-empirical coefficient. "
            "Historical -0.6 correlation at 2-month lag from Fed staff work; "
            "this backtest measures the specific coefficient shipped, not "
            "the correlation itself.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
