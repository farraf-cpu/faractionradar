"""New Home Sales backtest — v1 vs v1.1.

  v1:   HSN1F 3-month trend (K annualized).
  v1.1: v1 * (1 + MORTGAGE_SENSITIVITY * MORTGAGE30US_4wk_change_bp).

Tighter 4-week mortgage window vs Existing's 2-month, reflecting
new-home's faster rate reaction (90%+ mortgage-financed).
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

MORTGAGE_SENSITIVITY = -0.007  # match emit_newhome.py


def _release_proxy_date(obs_date_str: str) -> str:
    """Point-in-time cutoff = target obs date (see backtest_retail.py for
    the rationale). Same MORTGAGE30US conservatism as backtest_existing.py
    — live v1.1 would have current-month weekly prints; backtest excludes
    them. Preserves v1 vs v1.1 direction; understates v1.1 improvement."""
    return obs_date_str


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# NewHome backtest — FRED_API_KEY missing, aborted."

    newhome = fetch_fred_history(api_key, "HSN1F", limit=n + 20)
    mortgage = fetch_fred_history(api_key, "MORTGAGE30US", limit=120)
    if not newhome or len(newhome) < 5:
        return "# NewHome backtest — insufficient HSN1F history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(newhome) - 3)):
        target = newhome[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        # v1: 3-mo mean, in K (HSN1F reports thousands already)
        avail = slice_at_date(newhome, release_date)
        if len(avail) < 3:
            continue
        vals = obs_to_floats(avail[:3])
        if len(vals) < 3:
            continue
        v1_trend = statistics.mean(vals)

        # v1.1: mortgage-rate 4-week shock modulation (5-week window)
        v1_1_pred = None
        if mortgage:
            m_avail = slice_at_date(mortgage, release_date)
            if len(m_avail) >= 5:
                rates = obs_to_floats(m_avail[:5])
                if len(rates) >= 5:
                    recent = (rates[0] + rates[1]) / 2.0
                    lagged = (rates[3] + rates[4]) / 2.0
                    rate_change_bp = (recent - lagged) * 100.0
                    v1_1_pred = v1_trend * (1.0 + MORTGAGE_SENSITIVITY * rate_change_bp)

        # Actual: HSN1F level for target month
        try:
            actual = float(target["value"])
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
        "US New Home Sales (annualized, K)",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            f"- **NewHome-specific:** MORTGAGE_SENSITIVITY = "
            f"{MORTGAGE_SENSITIVITY}/bp is higher magnitude than "
            "Existing's -0.005 because new-home purchases are 90%+ "
            "mortgage-financed. 4-week window (vs Existing's 8-week) "
            "reflects faster rate reaction.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
