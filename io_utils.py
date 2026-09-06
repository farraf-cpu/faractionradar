"""Shared I/O helpers for the emit_*.py predictors.

Each emitter previously carried identical copies of:
- append_ledger: append one JSON row to predictions.jsonl
- post_to_worker: POST a prediction payload to the calendar-worker

118 predictors × ~25 duplicated lines each. Consolidating here.

Kept dependency-free (stdlib only).
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

__all__ = ["append_ledger", "post_to_worker"]

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"


def append_ledger(ledger_path: Path, payload: dict) -> None:
    """Append one compact JSON row to the predictions.jsonl ledger."""
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def post_to_worker(url: str, auth_key: str, payload: dict, tag: str = "emit") -> None:
    """POST a prediction payload to the calendar-worker /upload endpoint.
    Exits(3) on rejection so GHA fails loudly. `tag` prefixes log lines
    for grep-ability across the fleet."""
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": auth_key,
            "user-agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[{tag}] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[{tag}] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)
