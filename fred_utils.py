"""Shared FRED API helper for the lightweight emit_*.py predictors.

`src/fred_fetch.py` is a heavier pandas-based cache-to-disk fetcher used
by the NFP ML pipeline. The emit_*.py predictors don't need that scale —
they just want the last N observations from one series as a list of dicts.
17+ emitters had duplicated copies of the same 20-line helper; this
consolidates them into one function.

Kept dependency-free (stdlib only) so any predictor can import.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

__all__ = ["fetch_fred_observations"]

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"


def fetch_fred_observations(
    api_key: str,
    series_id: str,
    limit: int,
    tag: str = "emit",
) -> list[dict] | None:
    """Return the last `limit` observations from a FRED series, newest first.
    Filters out empty ('.' / '') values. Returns None on network error or
    when the response has no usable observations.

    `tag` is used only in the stderr log prefix — pass the emitter's
    identifier so failures are grep-able across the fleet.
    """
    url = (
        "https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={urllib.parse.quote(series_id)}"
        f"&api_key={urllib.parse.quote(api_key)}"
        f"&file_type=json&sort_order=desc&limit={limit}"
    )
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[{tag}] FRED {series_id} fetch failed: {e}", file=sys.stderr)
        return None
    obs = [
        o for o in (data.get("observations") or [])
        if o.get("value") not in (None, ".", "")
    ]
    return obs or None
