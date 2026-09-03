"""Gate for the daily Continuing Claims predict workflow. Same weekly cadence
as Initial Claims (Thursdays). Fires T-2 + T-1."""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta

VALID_DAYS_OUT = {2, 1}


def next_thursday(today: date) -> date:
    days_ahead = (3 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return today + timedelta(days=days_ahead)


def main() -> int:
    today = date.today()
    thu = next_thursday(today)
    days_out = (thu - today).days
    print(f"today={today.isoformat()} next_thursday={thu.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled Continuing Claims predict day (T-2 or T-1 only)")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"cclaims_release_date={thu.isoformat()}\n")
            f.write(f"cclaims_days_out={days_out}\n")
    print("run: Continuing Claims predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
