"""Gate for the daily CPI predict workflow.

CPI releases monthly, mid-month, typically Tuesday or Wednesday. Not fixed
day-of-month like NFP's first-Friday, so we resolve the next release date
from the calendar-worker's /public/upcoming-marquee endpoint (which is
FRED-driven, 45-day horizon).

Emits nfp-style outputs: cpi_release_date + cpi_days_out.

Exit 0 = run, 1 = skip (not a T-{7,4,3,2,1} day for CPI).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date, datetime

WORKER_URL = "https://faractionradar-calendar.faractionradar.workers.dev/public/upcoming-marquee"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

VALID_DAYS_OUT = {7, 4, 3, 2, 1}


def next_cpi_date(today: date) -> date | None:
    req = urllib.request.Request(WORKER_URL, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[should-run-cpi] failed to fetch upcoming-marquee: {e}", file=sys.stderr)
        return None
    items = data.get("items") or []
    # slug format: "cpi-YYYY-MM-DD". Pick the earliest CPI date >= today.
    cpis = []
    for it in items:
        if it.get("label") != "CPI":
            continue
        d_str = it.get("date")
        if not d_str:
            continue
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= today:
            cpis.append(d)
    if not cpis:
        return None
    return min(cpis)


def main() -> int:
    today = date.today()
    cpi = next_cpi_date(today)
    if cpi is None:
        print(f"[should-run-cpi] no CPI in upcoming-marquee horizon; skip")
        return 1

    days_out = (cpi - today).days
    print(f"today={today.isoformat()} next_cpi={cpi.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled CPI predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"cpi_release_date={cpi.isoformat()}\n")
            f.write(f"cpi_days_out={days_out}\n")
    print("run: CPI predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
