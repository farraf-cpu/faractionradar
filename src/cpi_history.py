"""Fetch historical CPI first-print series from ALFRED (FRED archive).

For each CPI release date (typically the 2nd Tuesday-Wednesday of each month
mid-morning ET, ~08:30 ET), fetch the CPIAUCSL vintage as-of that date. The
last data point in that vintage is the FIRST-PRINT headline CPI level for
the prior month — what will be reported on release day.

Analogous to src/alfred_fetch.py (which does the same for PAYEMS/NFP). Feeds
future Phase 2 CPI walk-forward backtest work.

Not called from any live workflow yet — this is a manual backfill script
you run once to populate data/raw/CPIAUCSL_FIRST_PRINT.csv, then re-run
periodically to append new months.

Usage:
  FRED_API_KEY=your_key python -m src.cpi_history
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
FIRST_PRINT_CACHE = RAW / "CPIAUCSL_FIRST_PRINT.csv"

ALFRED_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={sid}&vintage_date={dt}"


def cpi_release_dates(start_year: int = 2005, end_year: int = 2026) -> list[pd.Timestamp]:
    """CPI is typically released 08:30 ET on the second Tuesday or Wednesday
    of each month. We approximate as the 2nd Tuesday of each month — close
    enough for vintage lookup (the vintage_date param on ALFRED accepts any
    date; it returns the series as it existed on that date, so being off by
    a day or two doesn't matter for the first-print value)."""
    dates: list[pd.Timestamp] = []
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            first = pd.Timestamp(y, m, 1)
            # weekday(): Mon=0 .. Tue=1 .. Fri=4 .. Sun=6
            offset = (1 - first.weekday()) % 7
            first_tuesday = first + pd.Timedelta(days=offset)
            second_tuesday = first_tuesday + pd.Timedelta(days=7)
            if second_tuesday <= pd.Timestamp.now():
                dates.append(second_tuesday)
    return dates


def fetch_vintage_headline(sid: str, vintage_date: pd.Timestamp) -> dict | None:
    """Return the reported headline for this vintage: last-month level,
    prior-month level (same vintage), and computed m/m %-change."""
    url = ALFRED_URL.format(sid=sid, dt=vintage_date.date())
    r = requests.get(url, headers={"User-Agent": "Predictor/1.0"}, timeout=30)
    if r.status_code != 200:
        return None
    try:
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna().sort_values("date")
        if len(df) < 2:
            return None
        last = df.iloc[-1]
        prior = df.iloc[-2]
        prior_v = float(prior["value"])
        if prior_v <= 0:
            return None
        mom_pct = (float(last["value"]) - prior_v) / prior_v * 100.0
        return {
            "ref_month": pd.Timestamp(last["date"]),
            "ref_level": float(last["value"]),
            "prior_month": pd.Timestamp(prior["date"]),
            "prior_level": prior_v,
            "reported_mom_pct": mom_pct,
        }
    except Exception:
        return None


def build_first_print_series(sid: str = "CPIAUCSL",
                             start_year: int = 2005,
                             end_year: int = 2026,
                             cache: Path = FIRST_PRINT_CACHE,
                             rate_limit_sec: float = 0.3,
                             force_refresh: bool = False) -> pd.DataFrame:
    if cache.exists() and not force_refresh:
        print(f"[cached] using {cache}")
        return pd.read_csv(cache, parse_dates=["ref_month", "release_date", "prior_month"])

    release_dates = cpi_release_dates(start_year, end_year)
    print(f"Fetching {len(release_dates)} vintages of {sid}...")
    rows = []
    for i, rd in enumerate(release_dates):
        result = fetch_vintage_headline(sid, rd)
        if result is None:
            print(f"  [FAIL] vintage {rd.date()}")
            continue
        rows.append({
            "release_date": rd,
            "ref_month": result["ref_month"],
            "prior_month": result["prior_month"],
            "first_print_level": result["ref_level"],
            "prior_level_same_vintage": result["prior_level"],
            "reported_mom_pct": result["reported_mom_pct"],
        })
        if i % 20 == 0:
            print(f"  [{i:3d}/{len(release_dates)}] vintage={rd.date()} "
                  f"ref={result['ref_month'].date()} mom%={result['reported_mom_pct']:+.2f}")
        time.sleep(rate_limit_sec)

    df = pd.DataFrame(rows).drop_duplicates(subset="ref_month", keep="first").sort_values("ref_month")
    RAW.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache, index=False)
    print(f"\nSaved {len(df)} first-print CPI rows to {cache}")
    return df


if __name__ == "__main__":
    fp = build_first_print_series(start_year=2010, end_year=2026, force_refresh=True)
    print(f"\nFirst-print CPI series shape: {fp.shape}")
    print(f"Date range: {fp['ref_month'].min().date()} to {fp['ref_month'].max().date()}")
    print(f"\nLast 12 first prints (reported m/m on release day):")
    tail = fp.tail(12)[["release_date", "ref_month", "first_print_level", "reported_mom_pct"]].copy()
    tail["release_date"] = tail["release_date"].dt.date
    tail["ref_month"] = tail["ref_month"].dt.date
    print(tail.to_string(index=False))

    print("\nSummary stats (COVID masked):")
    covid_mask = (fp["ref_month"] < "2020-03-01") | (fp["ref_month"] > "2020-12-01")
    mom = fp.loc[covid_mask, "reported_mom_pct"].dropna()
    print(f"  n={len(mom)}")
    print(f"  mean:    {mom.mean():+.2f}pp")
    print(f"  std:     {mom.std():.2f}pp")
    print(f"  median:  {mom.median():+.2f}pp")
    print(f"  |mom|>0.5pp: {(mom.abs() > 0.5).sum()}")

    recent = fp[fp["ref_month"] >= "2022-06-01"]["reported_mom_pct"].dropna()
    print(f"\nPost-COVID (n={len(recent)}):")
    print(f"  mean:    {recent.mean():+.2f}pp")
    print(f"  std:     {recent.std():.2f}pp")
    print(f"  median:  {recent.median():+.2f}pp")
