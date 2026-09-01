"""Build monthly feature matrix + NFP MoM-change target.

Timing model — when predicting NFP for reference month t (released early t+1):
  - ADP(t)                 usable  (releases ~2 days before NFP)
  - Empire/Philly emp(t)   usable  (mid-month t release)
  - Jobless claims → aggregated over t   usable
  - UMich sentiment(t)     usable  (final release end of t)
  - Financial (t)          usable  (daily → monthly aggregate)
  - BLS Household + NFP sub-sectors: co-released with NFP → LAG 1 (use t-1 values)
  - JOLTS(t)               NOT usable → use JOLTS(t-1)  (JOLTS releases early t+2)
  - INDPRO/RSXFS/HOUST/PERMIT(t): released mid-late t+1, after NFP → LAG 1
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAW = Path("C:/Predictor/data/raw")
PROC = Path("C:/Predictor/data/processed")
PROC.mkdir(parents=True, exist_ok=True)

PREDICTION_MONTH = pd.Timestamp("2026-07-01")


def load(sid: str) -> pd.Series:
    df = pd.read_csv(RAW / f"{sid}.csv", parse_dates=["date"])
    s = df.set_index("date")["value"].sort_index()
    s.index = s.index.to_period("M").to_timestamp()
    return s.groupby(s.index).last()  # ensure unique monthly index


def load_raw(sid: str) -> pd.Series:
    """Load without monthly coercion — preserves weekly/daily resolution."""
    df = pd.read_csv(RAW / f"{sid}.csv", parse_dates=["date"])
    return df.set_index("date")["value"].sort_index()


def lag_months(s: pd.Series, months: int) -> pd.Series:
    """Shift the index forward by `months`. Value at t becomes labeled t + months.
    This is the RIGHT way to build lag features: it correctly extends the effective index
    so a Jul-2026 lag1 row exists (= Jun-2026 original value).
    """
    out = s.copy()
    out.index = out.index + pd.DateOffset(months=months)
    return out


def to_monthly_mean(s: pd.Series) -> pd.Series:
    """Resample daily/weekly to monthly mean, indexed month-start."""
    return s.resample("MS").mean()


def build_feature_matrix() -> pd.DataFrame:
    # ---------- TARGET ----------
    payems = load("PAYEMS")  # SA level, thousands
    nfp_change_k = payems.diff()

    features: dict[str, pd.Series] = {}

    # ---------- BLS CO-RELEASED (lag 1: released ON NFP day, so t-1 is what's known) ----------
    features["payems_yoy_lag1"]    = lag_months(payems.pct_change(12) * 100, 1)
    features["usspriv_chg_lag1"]   = lag_months(load("USPRIV").diff(), 1)
    features["manemp_chg_lag1"]    = lag_months(load("MANEMP").diff(), 1)
    features["uscons_chg_lag1"]    = lag_months(load("USCONS").diff(), 1)
    features["ustrade_chg_lag1"]   = lag_months(load("USTRADE").diff(), 1)
    features["usgovt_chg_lag1"]    = lag_months(load("USGOVT").diff(), 1)
    features["unrate_lag1"]        = lag_months(load("UNRATE"), 1)
    features["unrate_chg_lag1"]    = lag_months(load("UNRATE").diff(), 1)
    features["u6rate_lag1"]        = lag_months(load("U6RATE"), 1)
    features["civpart_lag1"]       = lag_months(load("CIVPART"), 1)
    features["ahetpi_yoy_lag1"]    = lag_months(load("AHETPI").pct_change(12) * 100, 1)
    features["awhaetp_lag1"]       = lag_months(load("AWHAETP"), 1)

    # ---------- ADP (contemporaneous t; ADP releases ~2 days before NFP) ----------
    adp = load("ADPMNUSNERSA") / 1000.0  # persons → thousands
    features["adp_level_k"] = adp
    features["adp_chg_k"]   = adp.diff()

    # ---------- Regional Fed employment (contemporaneous t; mid-month release) ----------
    features["empire_emp"] = load("NECDISA066MSFRBNY")
    features["philly_emp"] = load("NECDFSA066MSFRBPHI")

    # ---------- Sentiment (contemporaneous t; UMich final = end of month t) ----------
    features["umcsent"] = load("UMCSENT")

    # ---------- JOLTS (lag 1: JOLTS(t) releases early t+2, so JOLTS(t-1) usable) ----------
    for sid, name in [("JTSJOL", "jolts_openings"), ("JTSHIL", "jolts_hires"),
                      ("JTSTSL", "jolts_seps"), ("JTSQUL", "jolts_quits"),
                      ("JTSLDL", "jolts_layoffs")]:
        features[name] = lag_months(load(sid), 1)

    # ---------- JOLTS first-print vintage version (vintage-aware) ----------
    fp_path = RAW / "vintage_features.csv"
    if fp_path.exists():
        fp_df = pd.read_csv(fp_path, parse_dates=["date"]).set_index("date")
        fp_df.index = fp_df.index.to_period("M").to_timestamp()
        if "JTSJOL_fp" in fp_df.columns:
            features["jolts_openings_fp"] = lag_months(fp_df["JTSJOL_fp"], 1)
            # Also the surprise: (first-print - 3mo avg first-print)
            fp_series = fp_df["JTSJOL_fp"]
            features["jolts_fp_surprise"] = lag_months(fp_series - fp_series.rolling(3).mean(), 1)

    # ---------- Macro monthly (lag 1: released mid-late t+1, after NFP) ----------
    for sid, name in [("INDPRO", "indpro"), ("RSXFS", "rsxfs"),
                      ("HOUST", "houst"), ("PERMIT", "permit")]:
        s = load(sid)
        features[f"{name}_lag1"]     = lag_months(s, 1)
        features[f"{name}_yoy_lag1"] = lag_months(s.pct_change(12) * 100, 1)

    # ---------- Jobless claims (weekly → monthly mean, contemporaneous) ----------
    ic = load("ICSA")
    cc = load("CCSA")
    ic4w = load("IC4WSA")
    ic_m = to_monthly_mean(ic)
    cc_m = to_monthly_mean(cc)
    features["icsa_monthly_mean"] = ic_m
    features["ccsa_monthly_mean"] = cc_m
    features["ic4w_monthly_mean"] = to_monthly_mean(ic4w)
    features["icsa_chg"] = ic_m.diff()
    features["ccsa_chg"] = cc_m.diff()

    # ---------- REFERENCE-WEEK claims (week including 12th of month) ----------
    # BLS establishment-survey reference week = week containing the 12th. Claims filed
    # in this specific week are what determines the employment count for the month.
    # More predictive than monthly mean.
    def ref_week_claims(weekly: pd.Series) -> pd.Series:
        out = {}
        wk = weekly.sort_index()
        months = pd.date_range(wk.index.min().to_period("M").to_timestamp(),
                               wk.index.max().to_period("M").to_timestamp(), freq="MS")
        for mo in months:
            target_start = mo + pd.Timedelta(days=11)
            target_end = mo + pd.Timedelta(days=17)
            candidates = wk[(wk.index >= target_start) & (wk.index <= target_end)]
            if len(candidates) > 0:
                out[mo] = float(candidates.iloc[0])
        return pd.Series(out)

    ic_raw = load_raw("ICSA")
    cc_raw = load_raw("CCSA")
    features["icsa_ref_week"] = ref_week_claims(ic_raw)
    features["ccsa_ref_week"] = ref_week_claims(cc_raw)

    # ---------- ISM EMPLOYMENT (scraped, ~2024+; short history) ----------
    ism_path = RAW / "ISM_EMPLOYMENT_SCRAPED.csv"
    if ism_path.exists():
        ism = pd.read_csv(ism_path, parse_dates=["date"]).set_index("date").sort_index()
        ism.index = ism.index.to_period("M").to_timestamp()
        features["ism_mfg_emp"] = ism["mfg_employment_index"]
        features["ism_serv_emp"] = ism["services_employment_index"]
        features["ism_mfg_emp_chg"] = ism["mfg_employment_index"].diff()
        features["ism_serv_emp_chg"] = ism["services_employment_index"].diff()
        # composite: weighted by sector employment share (services ~85%, mfg ~10%)
        composite = 0.10 * ism["mfg_employment_index"] + 0.90 * ism["services_employment_index"]
        features["ism_composite_emp"] = composite

    # ---------- Financial daily → monthly mean (contemporaneous) ----------
    for sid, name in [("T10Y2Y", "yc_2s10s"), ("DGS10", "y10"),
                      ("FEDFUNDS", "ffr"), ("DCOILWTICO", "oil"),
                      ("VIXCLS", "vix"), ("T10YIE", "beie10")]:
        features[f"{name}_m"] = to_monthly_mean(load(sid))

    # ---------- Autoregressive NFP-change lags ----------
    features["nfp_chg_lag1"]  = lag_months(nfp_change_k, 1)
    features["nfp_chg_lag2"]  = lag_months(nfp_change_k, 2)
    features["nfp_chg_lag3"]  = lag_months(nfp_change_k, 3)
    features["nfp_chg_3m_avg"]  = lag_months(nfp_change_k.rolling(3).mean(), 1)
    features["nfp_chg_6m_avg"]  = lag_months(nfp_change_k.rolling(6).mean(), 1)
    features["nfp_chg_12m_avg"] = lag_months(nfp_change_k.rolling(12).mean(), 1)

    # ---------- ASSEMBLE with extended index (through prediction month + 1) ----------
    all_idx = pd.date_range("1948-01-01", PREDICTION_MONTH + pd.DateOffset(months=1), freq="MS")
    df = pd.DataFrame(index=all_idx)
    for col, s in features.items():
        s = s[~s.index.duplicated(keep="last")]
        df[col] = s.reindex(all_idx)
    df["target_nfp_chg_k"] = nfp_change_k.reindex(all_idx)

    df.index.name = "date"
    return df


if __name__ == "__main__":
    df = build_feature_matrix()
    df.to_csv(PROC / "features.csv")

    print(f"Feature matrix shape: {df.shape}")
    print(f"Date range: {df.index[0].date()} to {df.index[-1].date()}")

    tgt = df["target_nfp_chg_k"].dropna()
    print(f"\nTarget stats: n={len(tgt)}, mean={tgt.mean():.1f}K, std={tgt.std():.1f}K")

    # Prediction row for Jul 2026
    print(f"\n=== FEATURES AVAILABLE for {PREDICTION_MONTH.date()} prediction ===")
    row = df.loc[PREDICTION_MONTH]
    non_null = row.drop("target_nfp_chg_k").dropna()
    print(f"Non-null predictors: {len(non_null)}/{len(row)-1}")
    print(non_null.to_string())

    print(f"\nStill missing (require Jul-reference-month data or newer):")
    for c in df.columns.drop("target_nfp_chg_k"):
        if pd.isna(row[c]):
            print(f"  {c}")
