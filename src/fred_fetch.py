"""Pull FRED time series via public CSV endpoint. No API key required."""
from __future__ import annotations

import io
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"

SERIES = {
    "PAYEMS":   "Total Nonfarm Payrolls (SA, thousands) — TARGET SOURCE",
    "PAYNSA":   "Total Nonfarm Payrolls (NSA)",
    "USPRIV":   "Private Nonfarm Payrolls (SA)",
    "MANEMP":   "Manufacturing Employment",
    "USCONS":   "Construction Employment",
    "USTRADE":  "Retail Trade Employment",
    "USGOVT":   "Government Employment",
    "ADPMNUSNERSA": "ADP Nonfarm Private Employment (post-2022 redesign, SA)",
    "ICSA":     "Initial Jobless Claims (weekly, SA)",
    "CCSA":     "Continuing Jobless Claims (weekly, SA)",
    "IC4WSA":   "Initial Claims 4-Week Moving Avg",
    "NECDISA066MSFRBNY": "Empire State (NY Fed) Current Employees SA",
    "NECDFSA066MSFRBPHI": "Philly Fed Current Employment SA",
    "JTSJOL":   "JOLTS Job Openings",
    "JTSHIL":   "JOLTS Hires",
    "JTSTSL":   "JOLTS Total Separations",
    "JTSQUL":   "JOLTS Quits",
    "JTSLDL":   "JOLTS Layoffs & Discharges",
    "UNRATE":   "Unemployment Rate",
    "U6RATE":   "U6 Underemployment Rate",
    "CIVPART":  "Labor Force Participation Rate",
    "AHETPI":   "Avg Hourly Earnings, Production/Nonsupervisory",
    "AWHAETP":  "Avg Weekly Hours, Production/Nonsupervisory",
    "UMCSENT":  "U Michigan Consumer Sentiment",
    "INDPRO":   "Industrial Production Index",
    "RSXFS":    "Retail Sales Ex Food Services",
    "HOUST":    "Housing Starts",
    "PERMIT":   "Building Permits",
    "T10Y2Y":   "10Y-2Y Treasury Spread",
    "DGS10":    "10Y Treasury Yield",
    "FEDFUNDS": "Fed Funds Rate",
    "DEXUSEU":  "USD/EUR",
    "DCOILWTICO": "WTI Oil",
    "VIXCLS":   "VIX",
    "T10YIE":   "10Y Breakeven Inflation",
}


def fetch_series(sid: str, cache_dir: str | Path = "C:/Predictor/data/raw", timeout: int = 30) -> pd.DataFrame:
    """Fetch a single FRED series as a two-column DataFrame (date, value)."""
    url = FRED_CSV_URL.format(sid=sid)
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "Predictor/1.0"})
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df = df.dropna(subset=["date", "value"]).reset_index(drop=True)
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_dir / f"{sid}.csv", index=False)
    return df


def fetch_all(cache_dir: str | Path = "C:/Predictor/data/raw") -> dict[str, pd.DataFrame]:
    """Fetch every series in SERIES. Prints per-series status. Returns dict of DataFrames."""
    results: dict[str, pd.DataFrame] = {}
    for sid, desc in SERIES.items():
        try:
            df = fetch_series(sid, cache_dir=cache_dir)
            results[sid] = df
            last_date = df["date"].iloc[-1].date()
            last_val = df["value"].iloc[-1]
            print(f"[OK]   {sid:12s} n={len(df):5d} last={last_date} val={last_val:>14.3f}  # {desc}")
        except Exception as e:
            print(f"[FAIL] {sid:12s} {e}  # {desc}")
    return results


if __name__ == "__main__":
    print(f"Fetching {len(SERIES)} FRED series to C:/Predictor/data/raw/")
    print(f"Start: {datetime.now().isoformat(timespec='seconds')}\n")
    fetch_all()
    print(f"\nDone: {datetime.now().isoformat(timespec='seconds')}")
