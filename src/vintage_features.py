"""Build first-print vintage features for JOLTS + INDPRO + RSXFS.

Currently our features use REVISED values from FRED (smoothed, backward-looking).
The model was trained on this clean data but must predict using REAL-TIME (first-print)
values. This creates a subtle train/deploy mismatch that hurts accuracy.

Fix: use ALFRED to fetch first-vintage values for each month, replacing revised.
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import requests

RAW = Path("C:/Predictor/data/raw")

ALFRED_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id={sid}&vintage_date={dt}"

# For each series, we want the value for reference_month as reported ~1 month later
# (the first-print release date). Approximation: use vintage 30 days after ref_month
# for JOLTS (which releases ~5-6 weeks after ref month) — 45 days.
SERIES_RELEASE_LAG_DAYS = {
    "JTSJOL": 40,  # JOLTS Openings — highest single-series impact
}


def first_print_of_series(sid: str, ref_month: pd.Timestamp, lag_days: int) -> float | None:
    """For a reference month, fetch the value that was FIRST PRINTED for it.
    Approximation: use vintage = ref_month_end + lag_days."""
    vintage = ref_month + pd.DateOffset(months=1) + pd.Timedelta(days=lag_days)
    url = ALFRED_URL.format(sid=sid, dt=vintage.date())
    try:
        r = requests.get(url, headers={"User-Agent": "Predictor/1.0"}, timeout=30)
        if r.status_code != 200:
            return None
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna()
        # Get value for ref_month specifically
        match = df[df["date"] == ref_month]
        if len(match) == 0:
            return None
        return float(match.iloc[0]["value"])
    except Exception:
        return None


def build_first_print_series(sid: str, start: str = "2010-01-01",
                             end: str = "2026-06-01", rate_sec: float = 0.2) -> pd.Series:
    """Build a monthly series of first-vintage values."""
    lag = SERIES_RELEASE_LAG_DAYS.get(sid, 30)
    months = pd.date_range(start, end, freq="MS")
    values = {}
    for i, m in enumerate(months):
        v = first_print_of_series(sid, m, lag)
        if v is not None:
            values[m] = v
        if i % 20 == 0:
            print(f"    [{i:3d}/{len(months)}] {m.date()}: {v}")
        time.sleep(rate_sec)
    return pd.Series(values, name=f"{sid}_fp")


def build_all_vintage_features(cache_path: Path = RAW / "vintage_features.csv",
                               force: bool = False):
    if cache_path.exists() and not force:
        print(f"[cached] using {cache_path}")
        return pd.read_csv(cache_path, parse_dates=["date"]).set_index("date")

    out = pd.DataFrame()
    for sid in SERIES_RELEASE_LAG_DAYS.keys():
        print(f"\n=== Fetching first-print vintages for {sid} ===")
        s = build_first_print_series(sid)
        out[f"{sid}_fp"] = s
    out.index.name = "date"
    out.to_csv(cache_path)
    print(f"\nSaved vintage features to {cache_path}")
    return out


if __name__ == "__main__":
    df = build_all_vintage_features(force=True)
    print("\n=== Summary ===")
    print(f"Shape: {df.shape}")
    for c in df.columns:
        print(f"  {c}: {df[c].notna().sum()} non-null, last={df[c].dropna().index[-1].date() if df[c].notna().any() else 'None'}")
    print(f"\nTail:")
    print(df.tail(6).to_string())
