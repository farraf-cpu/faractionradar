"""Fetch FIRST-PRINT NFP values from ALFRED (FRED archive).

For each NFP release date (first Friday of each month), fetch the PAYEMS vintage
as-of that date. The last data point in that vintage is the FIRST-PRINT value
for the prior month — exactly what will be reported on TV/news.

This lets us train models on first-print targets, not revised.
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import requests

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
FIRST_PRINT_CACHE = RAW / "PAYEMS_FIRST_PRINT.csv"

ALFRED_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={sid}&vintage_date={dt}"


def nfp_release_dates(start_year: int = 2005, end_year: int = 2026) -> list[pd.Timestamp]:
    """NFP typically releases first Friday of each month. Return list of release dates."""
    dates = []
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            d = pd.Timestamp(y, m, 1)
            while d.weekday() != 4:
                d += pd.Timedelta(days=1)
            if d <= pd.Timestamp("2026-07-31"):
                dates.append(d)
    return dates


def fetch_vintage_headline(sid: str, vintage_date: pd.Timestamp) -> dict | None:
    """Return the reported headline: last-month level, prior-month level (same vintage),
    and their difference (= reported NFP change on that release day)."""
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
        return {
            "ref_month": pd.Timestamp(last["date"]),
            "ref_level": float(last["value"]),
            "prior_month": pd.Timestamp(prior["date"]),
            "prior_level": float(prior["value"]),
            "reported_change_k": float(last["value"] - prior["value"]),
        }
    except Exception:
        return None


def build_first_print_series(sid: str = "PAYEMS",
                             start_year: int = 2005,
                             end_year: int = 2026,
                             cache: Path = FIRST_PRINT_CACHE,
                             rate_limit_sec: float = 0.3,
                             force_refresh: bool = False) -> pd.DataFrame:
    if cache.exists() and not force_refresh:
        print(f"[cached] using {cache}")
        return pd.read_csv(cache, parse_dates=["ref_month", "release_date", "prior_month"])

    release_dates = nfp_release_dates(start_year, end_year)
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
            "reported_change_k": result["reported_change_k"],
        })
        if i % 20 == 0:
            print(f"  [{i:3d}/{len(release_dates)}] vintage={rd.date()} ref={result['ref_month'].date()} "
                  f"level={result['ref_level']:.0f} chg={result['reported_change_k']:+.1f}")
        time.sleep(rate_limit_sec)

    df = pd.DataFrame(rows).drop_duplicates(subset="ref_month", keep="first").sort_values("ref_month")
    df.to_csv(cache, index=False)
    print(f"\nSaved {len(df)} first-print rows to {cache}")
    return df


def compare_first_vs_revised(first_prints: pd.DataFrame,
                             revised_csv: Path = RAW / "PAYEMS.csv") -> pd.DataFrame:
    revised = pd.read_csv(revised_csv, parse_dates=["date"])
    revised = revised.rename(columns={"date": "ref_month", "value": "revised_value"})
    m = first_prints.merge(revised, on="ref_month", how="inner").sort_values("ref_month")
    # revised change: current-vintage change (from FRED)
    m["revised_chg_k"] = m["revised_value"].diff()
    # revision = revised - reported (headline reported that day)
    m["revision"] = m["revised_chg_k"] - m["reported_change_k"]
    return m


if __name__ == "__main__":
    fp = build_first_print_series(start_year=2010, end_year=2026, force_refresh=True)
    print(f"\nFirst-print series shape: {fp.shape}")
    print(f"Date range: {fp['ref_month'].min().date()} to {fp['ref_month'].max().date()}")
    print(f"\nLast 12 first prints (reported change on release day):")
    print(fp.tail(12)[["release_date", "ref_month", "first_print_level", "reported_change_k"]].to_string(index=False))

    # Compare reported with revised
    cmp = compare_first_vs_revised(fp)
    cmp.to_csv(RAW / "PAYEMS_FIRST_VS_REVISED.csv", index=False)
    print(f"\n=== FIRST-PRINT vs REVISED analysis ({len(cmp)} months) ===")

    # Mask COVID
    cmp_no_covid = cmp[(cmp["ref_month"] < "2020-03-01") | (cmp["ref_month"] > "2020-12-01")]

    rev = cmp_no_covid["revision"].dropna()
    print(f"\nAll months (COVID masked, n={len(rev)}):")
    print(f"  Mean revision:  {rev.mean():+.1f} K   (+ = revised UP from first print)")
    print(f"  Std revision:   {rev.std():.1f} K")
    print(f"  Median rev:     {rev.median():+.1f} K")
    print(f"  Abs mean:       {rev.abs().mean():.1f} K")
    print(f"  |Rev| >50K:     {(rev.abs() > 50).sum()} of {len(rev)} months")
    print(f"  |Rev| >100K:    {(rev.abs() > 100).sum()} of {len(rev)} months")

    recent = cmp[cmp["ref_month"] >= "2022-06-01"]["revision"].dropna()
    print(f"\nPost-COVID (n={len(recent)}):")
    print(f"  Mean:      {recent.mean():+.1f} K")
    print(f"  Std:       {recent.std():.1f} K")
    print(f"  Median:    {recent.median():+.1f} K")
    print(f"  Abs mean:  {recent.abs().mean():.1f} K")

    # Show recent examples
    print(f"\nLast 12 months first-print vs revised:")
    show = cmp.tail(12)[["ref_month", "reported_change_k", "revised_chg_k", "revision"]].copy()
    show["ref_month"] = show["ref_month"].dt.date
    print(show.to_string(index=False))
