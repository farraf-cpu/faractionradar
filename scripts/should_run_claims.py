"""Gate for the daily Initial Jobless Claims predict workflow.

Weekly cadence (every Thursday) so we don't need the upcoming-marquee
horizon lookup — just check date arithmetic. Fire T-2 (Tuesday) and T-1
(Wednesday) before Thursday release. Skip on weekends + Thursday-Monday.
"""
from __future__ import annotations

import os
import sys
from datetime import date, timedelta

VALID_DAYS_OUT = {2, 1}  # Weekly release; two cadence slots max


def next_thursday(today: date) -> date:
    """Return the next upcoming Thursday. If today is Thursday, returns
    NEXT Thursday (7 days out) — release hasn't fired yet at midnight."""
    # weekday(): Mon=0..Thu=3..Sun=6
    days_ahead = (3 - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # today IS Thursday — target NEXT week (release for today already fired at 08:30)
    return today + timedelta(days=days_ahead)


def main() -> int:
    today = date.today()
    thu = next_thursday(today)
    days_out = (thu - today).days
    print(f"today={today.isoformat()} next_thursday={thu.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled Claims predict day (T-2 or T-1 only)")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"claims_release_date={thu.isoformat()}\n")
            f.write(f"claims_days_out={days_out}\n")
    print("run: Claims predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
