"""CB Consumer Confidence backtest — v1 vs v1.1.

  v1:   naive anchor (previous-month CB Confidence value).
  v1.1: anchor * (1 + UMICH_CB_CORRELATION * UMCSENT_2mo_momentum).

CB Confidence itself is proprietary (not on FRED), so we substitute
FRED's CSCICP03USM665S (OECD Consumer Confidence Composite for US) as
a proxy for the "actual." UMCSENT is FRED-published. Consensus NOT
backtested (data unavailable).
"""
from __future__ import annotations

import os
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

UMICH_CB_CORRELATION = 0.75  # match emit_confidence.py

# CB Confidence proxy on FRED. This is OECD's harmonized US series;
# scale differs from CB's 1985=100 index but tracks direction.
CB_PROXY_SERIES = "CSCICP03USM665S"


def _release_proxy_date(obs_date_str: str) -> str:
    """Point-in-time cutoff = target obs date (see backtest_retail.py for
    the rationale). Conservative on UMCSENT: same-month UMCSENT Prelim
    releases 2nd Friday of the month, ~2 weeks BEFORE CB Confidence,
    so live v1.1 would have current-month UMCSENT. Preserves v1 vs v1.1
    direction; understates v1.1 improvement here more materially since
    UMCSENT current-month is the freshest input v1.1 uses."""
    return obs_date_str


def run(n: int = 24) -> str:
    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        return "# Confidence backtest — FRED_API_KEY missing, aborted."

    cb = fetch_fred_history(api_key, CB_PROXY_SERIES, limit=n + 20)
    umcsent = fetch_fred_history(api_key, "UMCSENT", limit=n + 20)
    if not cb or len(cb) < 5:
        return f"# Confidence backtest — insufficient {CB_PROXY_SERIES} history."

    rows: list[BacktestRow] = []
    for i in range(1, min(n + 1, len(cb) - 3)):
        target = cb[i]
        target_date = target["date"]
        release_date = _release_proxy_date(target_date)

        # v1: naive anchor = previous month's value
        cb_avail = slice_at_date(cb, release_date)
        if len(cb_avail) < 1:
            continue
        anchor_vals = obs_to_floats(cb_avail[:1])
        if not anchor_vals:
            continue
        v1_anchor = anchor_vals[0]

        # v1.1: apply UMCSENT 2-mo momentum
        v1_1_pred = None
        if umcsent:
            umich_avail = slice_at_date(umcsent, release_date)
            if len(umich_avail) >= 3:
                umich_vals = obs_to_floats(umich_avail[:3])
                if len(umich_vals) == 3 and umich_vals[2] > 0:
                    momentum = (umich_vals[0] - umich_vals[2]) / umich_vals[2]
                    v1_1_pred = v1_anchor * (1.0 + UMICH_CB_CORRELATION * momentum)

        # Actual: the CB proxy target
        try:
            actual = float(target["value"])
        except (ValueError, KeyError):
            continue

        rows.append(BacktestRow(
            release_date=release_date,
            v1_pred=v1_anchor,
            v1_1_pred=v1_1_pred,
            actual=actual,
        ))

    rows.sort(key=lambda r: r.release_date)
    v1_summary = BacktestSummary.from_errors("v1", [r.v1_err for r in rows])
    v1_1_summary = BacktestSummary.from_errors("v1.1", [r.v1_1_err for r in rows])

    return format_report(
        "US CB Consumer Confidence (OECD proxy series)",
        rows, [v1_summary, v1_1_summary],
        caveats=DEFAULT_CAVEATS + (
            f"- **Confidence proxy:** actual is FRED {CB_PROXY_SERIES} "
            "(OECD harmonized), NOT the Conference Board index. Scale "
            "differs but direction tracks. Real CB Confidence is proprietary "
            "and not on FRED, so absolute-value backtest is impossible; "
            "this measures directional accuracy of the sub-model.\n"
            f"- **Confidence-specific:** UMICH_CB_CORRELATION = "
            f"{UMICH_CB_CORRELATION} is the pre-empirical coefficient.\n"
        ),
    )


if __name__ == "__main__":
    print(run())
