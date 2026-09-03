"""Gate for the daily Retail Sales predict workflow."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date, datetime

WORKER_URL = "https://faractionradar-calendar.faractionradar.workers.dev/public/upcoming-marquee"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
VALID_DAYS_OUT = {7, 4, 3, 2, 1}


def next_retail_date(today: date) -> date | None:
    req = urllib.request.Request(WORKER_URL, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[should-run-retail] failed to fetch: {e}", file=sys.stderr)
        return None
    items = data.get("items") or []
    retails = []
    for it in items:
        if it.get("label") != "Retail":
            continue
        d_str = it.get("date")
        if not d_str:
            continue
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= today:
            retails.append(d)
    if not retails:
        return None
    return min(retails)


def main() -> int:
    today = date.today()
    r = next_retail_date(today)
    if r is None:
        print("[should-run-retail] no Retail Sales in upcoming-marquee horizon; skip")
        return 1

    days_out = (r - today).days
    print(f"today={today.isoformat()} next_retail={r.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled Retail predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"retail_release_date={r.isoformat()}\n")
            f.write(f"retail_days_out={days_out}\n")
    print("run: Retail predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
