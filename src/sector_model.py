"""Sector decomposition model for NFP.

Break NFP into major sectors, model each separately, sum for total.
Each sector uses its own set of predictors. Aggregate prediction from
sector-level models often beats a single aggregate model.

Sectors (thousands of jobs, June 2026 levels):
  MANEMP   Manufacturing               12,598
  USCONS   Construction                 8,331
  USTRADE  Retail Trade                15,459
  USTPU    Trade/Transport/Utilities   28,728 (includes USTRADE)
  USINFO   Information                  2,774
  USFIRE   Financial activities         9,104
  USPBS    Professional & Business    22,507
  USEHS    Education & Health         27,973
  USLAH    Leisure & Hospitality      16,951
  USMINE   Mining & Logging              607
  USSERV   Other Services              6,040
  USGOVT   Government                 23,371
  ---
  Note: PAYEMS = sum of USGOVT + all private above (approximately)
"""
from __future__ import annotations

import sys
sys.path.insert(0, "C:/Predictor")

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.build_features import build_feature_matrix, load, load_raw, lag_months, to_monthly_mean, PREDICTION_MONTH
from src.models import mask_covid, COVID_START, COVID_END
from src.bridge_backtest import JULY_OVERRIDES

RAW = Path("C:/Predictor/data/raw")
PROC = Path("C:/Predictor/data/processed")

# Sector series with sector-specific predictor sets. Predictors must be present
# in the feature matrix (or added inline).
SECTORS = {
    "MANEMP": {
        "predictors": ["ism_mfg_emp", "indpro_lag1", "empire_emp", "philly_emp", "y10_m", "oil_m", "manemp_chg_lag1"],
        "avg_share": 0.078,  # ~7.8% of total NFP
    },
    "USCONS": {
        "predictors": ["houst_lag1", "permit_lag1", "y10_m", "uscons_chg_lag1", "nfp_chg_lag1"],
        "avg_share": 0.052,
    },
    "USTPU": {   # trade, transport, utilities (includes retail)
        "predictors": ["rsxfs_yoy_lag1", "adp_chg_k", "icsa_ref_week", "empire_emp", "ism_serv_emp"],
        "avg_share": 0.181,
    },
    "USINFO": {
        "predictors": ["adp_chg_k", "nfp_chg_lag1", "ism_serv_emp"],
        "avg_share": 0.017,
    },
    "USFIRE": {
        "predictors": ["adp_chg_k", "y10_m", "yc_2s10s_m", "nfp_chg_lag1", "ism_serv_emp"],
        "avg_share": 0.057,
    },
    "USPBS": {
        "predictors": ["adp_chg_k", "empire_emp", "philly_emp", "umcsent", "icsa_ref_week", "ism_serv_emp"],
        "avg_share": 0.142,
    },
    "USEHS": {
        # education & health is the LARGEST private sector, very inelastic
        "predictors": ["nfp_chg_lag1", "nfp_chg_3m_avg", "adp_chg_k", "ism_serv_emp"],
        "avg_share": 0.176,
    },
    "USLAH": {
        # leisure & hospitality — sensitive to consumer confidence + services PMI
        "predictors": ["umcsent", "adp_chg_k", "rsxfs_yoy_lag1", "nfp_chg_lag1", "ism_serv_emp"],
        "avg_share": 0.107,
    },
    "USMINE": {
        "predictors": ["oil_m", "indpro_lag1", "nfp_chg_lag1"],
        "avg_share": 0.004,
    },
    "USSERV": {
        "predictors": ["adp_chg_k", "nfp_chg_lag1", "umcsent"],
        "avg_share": 0.038,
    },
    "USGOVT": {
        "predictors": ["nfp_chg_lag1", "nfp_chg_3m_avg"],
        "avg_share": 0.147,
    },
}


def build_sector_target(sid: str) -> pd.Series:
    """Return sector MoM change in thousands."""
    return load(sid).diff()


def fit_sector_model(sid: str, spec: dict, df: pd.DataFrame,
                     train_start=pd.Timestamp("2010-01-01"),
                     train_end=None) -> tuple[float, float, dict]:
    """Fit sector-specific regression using post-COVID data. Return (pred, rmse, coefs)."""
    tgt = build_sector_target(sid)
    d = df.copy()
    d[f"target_{sid}_chg"] = tgt.reindex(d.index)
    d = mask_covid(d)
    d = d[(d.index >= pd.Timestamp("2022-06-01"))
          & (d.index < (train_end or PREDICTION_MONTH))]
    d = d.dropna(subset=[f"target_{sid}_chg"] + spec["predictors"])
    if len(d) < 20:
        return None, None, {}

    X = d[spec["predictors"]].values
    y = d[f"target_{sid}_chg"].values
    m = LinearRegression().fit(X, y)
    resid = y - m.predict(X)
    rmse = float(np.sqrt(np.mean(resid ** 2)))

    # Predict for prediction month
    row = df.loc[[PREDICTION_MONTH], spec["predictors"]].copy()
    for c in spec["predictors"]:
        if pd.isna(row[c].iloc[0]):
            row[c] = d[c].iloc[-1]
    pred = float(m.predict(row.values)[0])
    coefs = dict(zip(spec["predictors"], m.coef_))
    return pred, rmse, coefs


def run():
    print("=" * 78)
    print("SECTOR DECOMPOSITION MODEL — sum of sector-specific regressions")
    print("=" * 78)

    df = build_feature_matrix()
    for c, v in JULY_OVERRIDES.items():
        if c in df.columns:
            df.at[PREDICTION_MONTH, c] = v

    results = []
    total_pred = 0.0
    total_var = 0.0

    for sid, spec in SECTORS.items():
        pred, rmse, coefs = fit_sector_model(sid, spec, df)
        if pred is None:
            print(f"  [SKIP] {sid} — insufficient data")
            continue
        results.append({"sector": sid, "pred_k": pred, "rmse_k": rmse,
                        "avg_share_pct": spec["avg_share"] * 100})
        total_pred += pred
        total_var += rmse ** 2  # assumes independent errors (upper bound on var)
        print(f"  {sid:8s}  {pred:+7.1f} K   (RMSE {rmse:4.0f}K, share {spec['avg_share']*100:.1f}%)")
        print(f"           coefs: " + ", ".join(f"{k}={v:+.3f}" for k, v in coefs.items()))

    total_rmse = float(np.sqrt(total_var))
    print(f"\n  SUM (all sectors) = {total_pred:+.1f} K  (upper-bound RMSE {total_rmse:.0f} K)")

    # Save results
    out = pd.DataFrame(results)
    out.to_csv(PROC / "sector_decomposition.csv", index=False)
    summary = {"total_pred_k": total_pred, "upper_bound_rmse_k": total_rmse,
               "n_sectors": len(results)}
    pd.DataFrame([summary]).to_csv(PROC / "sector_summary.csv", index=False)
    return summary


if __name__ == "__main__":
    run()
