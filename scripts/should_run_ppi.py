"""Gate for the daily PPI predict workflow. Same shape as CPI/FOMC gates:
hit the worker's /public/upcoming-marquee, find next PPI release date,
check if today is T-{7,4,3,2,1} out. Exit 0 = run, 1 = skip.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date, datetime

WORKER_URL = "https://faractionradar-calendar.faractionradar.workers.dev/public/upcoming-marquee"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

VALID_DAYS_OUT = {7, 4, 3, 2, 1, 0}   # 0 = release-day T-0 refresh


def next_ppi_date(today: date) -> date | None:
    req = urllib.request.Request(WORKER_URL, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[should-run-ppi] failed to fetch upcoming-marquee: {e}", file=sys.stderr)
        return None
    items = data.get("items") or []
    ppis = []
    for it in items:
        if it.get("label") != "PPI":
            continue
        d_str = it.get("date")
        if not d_str:
            continue
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= today:
            ppis.append(d)
    if not ppis:
        return None
    return min(ppis)


def main() -> int:
    today = date.today()
    ppi = next_ppi_date(today)
    if ppi is None:
        print("[should-run-ppi] no PPI in upcoming-marquee horizon; skip")
        return 1

    days_out = (ppi - today).days
    print(f"today={today.isoformat()} next_ppi={ppi.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled PPI predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"ppi_release_date={ppi.isoformat()}\n")
            f.write(f"ppi_days_out={days_out}\n")
    print("run: PPI predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
