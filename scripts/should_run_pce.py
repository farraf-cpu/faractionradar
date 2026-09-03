"""Gate for the daily PCE predict workflow. Hit /public/upcoming-marquee,
find next PCE release date, check if today is T-{7,4,3,2,1} out.
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


def next_pce_date(today: date) -> date | None:
    req = urllib.request.Request(WORKER_URL, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[should-run-pce] failed to fetch upcoming-marquee: {e}", file=sys.stderr)
        return None
    items = data.get("items") or []
    pces = []
    for it in items:
        if it.get("label") != "PCE":
            continue
        d_str = it.get("date")
        if not d_str:
            continue
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= today:
            pces.append(d)
    if not pces:
        return None
    return min(pces)


def main() -> int:
    today = date.today()
    pce = next_pce_date(today)
    if pce is None:
        print("[should-run-pce] no PCE in upcoming-marquee horizon; skip")
        return 1

    days_out = (pce - today).days
    print(f"today={today.isoformat()} next_pce={pce.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled PCE predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"pce_release_date={pce.isoformat()}\n")
            f.write(f"pce_days_out={days_out}\n")
    print("run: PCE predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
