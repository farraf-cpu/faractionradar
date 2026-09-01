"""Fetch ForexFactory this-week + next-week JSON and POST to calendar-worker
/upload-events.

Runs on GitHub Actions to bypass Cloudflare edge → Fastly 429 blocks.
GHA runners have residential-ish IPs that Fastly doesn't blocklist.

Env (set by workflow):
  UPLOAD_AUTH_KEY       — matches worker's UPLOAD_AUTH_KEY secret
  CALENDAR_WORKER_URL   — e.g. https://faractionradar-calendar.faractionradar.workers.dev

Exit codes:
  0 = both feeds succeeded and POSTed
  1 = both feeds failed to fetch (upstream 4xx/5xx)
  2 = missing required env
  3 = POST rejected by worker
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

FF_URLS = {
    "thisWeek": "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
    "nextWeek": "https://nfs.faireconomy.media/ff_calendar_nextweek.json",
}
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[fetch-calendar] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def fetch_json(url: str) -> tuple[list | None, str]:
    """Returns (events, status). status = 'ok' or 'error: ...'."""
    req = urllib.request.Request(
        url,
        headers={
            "user-agent": UA,
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            body = res.read().decode("utf-8")
            data = json.loads(body)
            if not isinstance(data, list):
                return None, "error: non-array response"
            return data, "ok"
    except urllib.error.HTTPError as e:
        return None, f"error: HTTP {e.code}"
    except Exception as e:
        return None, f"error: {type(e).__name__}: {e}"


def main() -> int:
    upload_key = require_env("UPLOAD_AUTH_KEY")
    worker_url = require_env("CALENDAR_WORKER_URL").rstrip("/") + "/upload-events"

    this_week, this_status = fetch_json(FF_URLS["thisWeek"])
    next_week, next_status = fetch_json(FF_URLS["nextWeek"])
    print(f"[fetch-calendar] thisWeek: {this_status} ({len(this_week) if this_week else 0} events)")
    print(f"[fetch-calendar] nextWeek: {next_status} ({len(next_week) if next_week else 0} events)")

    if this_week is None and next_week is None:
        print("[fetch-calendar] both feeds failed — nothing to upload", file=sys.stderr)
        return 1

    payload = {
        "thisWeek": this_week or [],
        "nextWeek": next_week or [],
        "fetchedAt": datetime.now(timezone.utc).isoformat(),
        "sourceStatus": {"thisWeek": this_status, "nextWeek": next_status},
    }
    body = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        worker_url,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": upload_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            resp_body = res.read().decode("utf-8")
            print(f"[fetch-calendar] worker → {res.status} {res.reason}")
            print(f"[fetch-calendar] response: {resp_body[:400]}")
            return 0
    except urllib.error.HTTPError as e:
        print(f"[fetch-calendar] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
