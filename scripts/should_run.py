"""Gate for the daily NFP predict workflow.

NFP releases on the first Friday of each month at 08:30 ET. We want the
predictor to run at T-7, T-4, T-3, T-2, T-1 days ahead. Encoding this in
cron is painful; instead we cron daily and let this script exit 0 (run)
or 1 (skip) based on the current UTC date.

Also emits the target release date + days-out via GITHUB_OUTPUT so the
workflow can pass them into emit.py as env vars.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta


VALID_DAYS_OUT = {7, 4, 3, 2, 1, 0}   # 0 = T-0 fire on release day (see cron 10:15 UTC)


def next_nfp_friday(today: date) -> date:
    """First Friday of the month for `today` if today <= that Friday, else
    first Friday of next month."""
    def first_friday_of(year: int, month: int) -> date:
        first = date(year, month, 1)
        # weekday(): Mon=0 .. Fri=4 .. Sun=6
        offset = (4 - first.weekday()) % 7
        return first + timedelta(days=offset)

    this_month = first_friday_of(today.year, today.month)
    if today <= this_month:
        return this_month
    ny, nm = (today.year + 1, 1) if today.month == 12 else (today.year, today.month + 1)
    return first_friday_of(ny, nm)


def main() -> int:
    today = date.today()
    nfp = next_nfp_friday(today)
    days_out = (nfp - today).days

    print(f"today={today.isoformat()} next_nfp={nfp.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"nfp_release_date={nfp.isoformat()}\n")
            f.write(f"nfp_days_out={days_out}\n")
    print("run: predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
