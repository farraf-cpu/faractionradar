"""Gate for the daily German IFO predict workflow."""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import date, datetime

WORKER_URL = "https://faractionradar-calendar.faractionradar.workers.dev/public/upcoming-marquee"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"
VALID_DAYS_OUT = {7, 4, 3, 2, 1, 0}   # 0 = release-day T-0 refresh


def next_deifo_date(today: date) -> date | None:
    req = urllib.request.Request(WORKER_URL, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[should-run-deifo] failed to fetch: {e}", file=sys.stderr)
        return None
    items = data.get("items") or []
    dates = []
    for it in items:
        if it.get("label") != "DE IFO":
            continue
        d_str = it.get("date")
        if not d_str:
            continue
        try:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d >= today:
            dates.append(d)
    if not dates:
        return None
    return min(dates)


def main() -> int:
    today = date.today()
    ev = next_deifo_date(today)
    if ev is None:
        print("[should-run-deifo] no DE IFO in upcoming-marquee horizon; skip")
        return 1

    days_out = (ev - today).days
    print(f"today={today.isoformat()} next_deifo={ev.isoformat()} days_out={days_out}")

    if days_out not in VALID_DAYS_OUT:
        print("skip: not a scheduled DE IFO predict day")
        return 1

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"deifo_release_date={ev.isoformat()}\n")
            f.write(f"deifo_days_out={days_out}\n")
    print("run: DE IFO predict day matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
