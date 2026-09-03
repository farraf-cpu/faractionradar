"""Gate for the daily ADP predict workflow.

ADP releases on the Wednesday before BLS NFP Friday. Since NFP is first-
Friday-of-month, ADP is the Wednesday 2 days before that (so ~1st Wed of
the month unless month starts on Fri/Sat/Sun).

Compute the next NFP first-Friday, subtract 2 days = next ADP Wednesday.
Fire T-{7,4,3,2,1} slots like the other monthly predictors.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta

VALID_DAYS_OUT = {7, 4, 3, 2, 1}


def next_nfp_friday(today: date) -> date:
    """First Friday of the month for `today` if today <= that Friday, else
    first Friday of next month."""
    def first_friday_of(year: int, month: int) -> date:
        first = date(year, month, 1)
        offset = (4 - first.weekday()) % 7
        return first + timedelta(days=offset)

    this_month = first_friday_of(today.year, today.month)
    if today <= this_month:
        return this_month
    ny, nm = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return first_friday_of(ny, nm)


def next_adp_wednesday(today: date) -> date:
    """Wednesday 2 days before the next NFP Friday. If today is already
    past that Wednesday but not past NFP, return next month's ADP."""
    nfp = next_nfp_friday(today)
    adp = nfp - timedelta(days=2)  # Wed before NFP Fri
    if today > adp:
        # This month's ADP already fired — target next NFP cycle
        ny, nm = (nfp.year + 1, 1) if nfp.month == 12 else (nfp.year, nfp.month + 1)
        first = date(ny, nm, 1)
        offset = (4 - first.weekday()) % 7
        return first + timedelta(days=offset) - timedelta(days=2)
    return adp


def main() -> int:
    today = date.today()
    adp = next_adp_wednesday(today)
    days_out = (adp - today).days
    print(f"today={today.isoformat()} next_adp={adp.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled ADP predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"adp_release_date={adp.isoformat()}\n")
            f.write(f"adp_days_out={days_out}\n")
    print("run: ADP predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
