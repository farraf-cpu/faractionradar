"""UMich Consumer Sentiment backtest — v1 vs v1.1.

  v1:   UMCSENT 3-month trend (mean of last 3 levels).
  v1.1: v1 + WTI oil-shock (trend + OIL_SHOCK_COEFF * MCOILWTICO m/m).

Both are level predictions (index points 30-110). Consensus + auto-tune
NOT backtested here (data unavailable). See README for caveats.
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

OIL_SHOCK_COEFF = -0.4  # match emit_umich.py


def _release_proxy_date(obs_date_str: str) -> str:
    """Point-in-time cutoff = target obs date (see backtest_retail.py for
    the rationale). Conservative on WTI: same-month MCOILWTICO is
    excluded, though live UMich at 2nd-Friday release WOULD have that
    reading. Preserves v1 vs v1.1 direction; understates v1.1 improvement."""
    return obs_date_str


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# UMich backtest — FRED_API_KEY missing, aborted."

    umcsent = fetch_fred_history(api_key, "UMCSENT", limit=n + 20)
    wti = fetch_fred_history(api_key, "MCOILWTICO", limit=n + 20)
    if not umcsent or len(umcsent) < 5:
        return "# UMich backtest — insufficient UMCSENT history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(umcsent) - 3)):
        target = umcsent[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        avail = slice_at_date(umcsent, release_date)
        if len(avail) < 3:
            continue
        vals = obs_to_floats(avail[:3])
        if len(vals) < 3:
            continue
        v1_trend = statistics.mean(vals)

        # v1.1: apply oil shock
        v1_1_pred = None
        if wti:
            wti_avail = slice_at_date(wti, release_date)
            if len(wti_avail) >= 2:
                wti_vals = obs_to_floats(wti_avail[:2])
                if len(wti_vals) == 2 and wti_vals[1] > 0:
                    wti_mom = (wti_vals[0] - wti_vals[1]) / wti_vals[1] * 100.0
                    v1_1_pred = v1_trend + OIL_SHOCK_COEFF * wti_mom

        # Actual: the target UMCSENT level
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
        "US UMich Consumer Sentiment (Preliminary)",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            f"- **UMich-specific:** OIL_SHOCK_COEFF = {OIL_SHOCK_COEFF} "
            "is the pre-empirical coefficient shipped in emit_umich.py. "
            "Actual sensitivity is regime-dependent; sensitivity sweep "
            "is a follow-up.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
