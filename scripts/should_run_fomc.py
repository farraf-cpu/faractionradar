"""Gate for the daily FOMC predict workflow.

FOMC meetings are hardcoded in the calendar-worker (federalreserve.gov
publishes the schedule annually). Same resolution as CPI — hit
/public/upcoming-marquee, find next FOMC date, check days-out.

Exit 0 = run, 1 = skip.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date, datetime

WORKER_URL = "https://faractionradar-calendar.faractionradar.workers.dev/public/upcoming-marquee"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

VALID_DAYS_OUT = {7, 4, 3, 2, 1, 0}   # 0 = release-day T-0 pre-release refresh


def next_fomc_date(today: date) -> date | None:
    req = urllib.request.Request(WORKER_URL, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[should-run-fomc] failed to fetch upcoming-marquee: {e}", file=sys.stderr)
        return None
    items = data.get("items") or []
    fomcs = []
    for it in items:
        if it.get("label") != "FOMC":
            continue
        d_str = it.get("date")
        if not d_str:
            continue
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= today:
            fomcs.append(d)
    if not fomcs:
        return None
    return min(fomcs)


def main() -> int:
    today = date.today()
    fomc = next_fomc_date(today)
    if fomc is None:
        print("[should-run-fomc] no FOMC in upcoming-marquee horizon; skip")
        return 1

    days_out = (fomc - today).days
    print(f"today={today.isoformat()} next_fomc={fomc.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled FOMC predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"fomc_release_date={fomc.isoformat()}\n")
            f.write(f"fomc_days_out={days_out}\n")
    print("run: FOMC predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
