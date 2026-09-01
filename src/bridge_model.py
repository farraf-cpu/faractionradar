"""Bridge equation model — pure ADP-implied NFP.

The classic Fed nowcasting approach: regress BLS NFP change on ADP change alone.
Historical beta is typically 0.5-0.7. This gives us a "pure ADP signal" prediction
that isn't diluted by correlated features in a multivariate model.
"""
from __future__ import annotations

import sys
sys.path.insert(0, "C:/Predictor")

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.models import load_features, mask_covid

PROC = Path("C:/Predictor/data/processed")


def fit_adp_bridge(df: pd.DataFrame, train_start=pd.Timestamp("2010-01-01"),
                   train_end=pd.Timestamp("2026-07-01"), post_covid_only=True):
    """Fit NFP_change ~ ADP_change. Returns (alpha, beta, resid_std, sample_size)."""
    d = df.loc[train_start:train_end - pd.DateOffset(months=1)].copy()
    d = mask_covid(d)
    d = d.dropna(subset=["target_nfp_chg_k", "adp_chg_k"])
    if post_covid_only:
        d = d[d.index >= pd.Timestamp("2022-06-01")]
    X = d[["adp_chg_k"]].values
    y = d["target_nfp_chg_k"].values
    m = LinearRegression().fit(X, y)
    y_hat = m.predict(X)
    resid = y - y_hat
    return {
        "alpha": float(m.intercept_),
        "beta": float(m.coef_[0]),
        "n": len(d),
        "resid_std": float(np.std(resid, ddof=1)),
        "r2": float(m.score(X, y)),
        "training_window": (d.index.min(), d.index.max()),
    }


def fit_multibridge(df, train_start=pd.Timestamp("2010-01-01"),
                    train_end=pd.Timestamp("2026-07-01"), post_covid_only=True):
    """Bridge with ADP + jobless claims + Empire + Philly (all high-signal, contemporaneous)."""
    cols = ["adp_chg_k", "icsa_monthly_mean", "ccsa_monthly_mean",
            "empire_emp", "philly_emp"]
    d = df.loc[train_start:train_end - pd.DateOffset(months=1)].copy()
    d = mask_covid(d)
    d = d.dropna(subset=["target_nfp_chg_k"] + cols)
    if post_covid_only:
        d = d[d.index >= pd.Timestamp("2022-06-01")]
    X = d[cols].values
    y = d["target_nfp_chg_k"].values
    m = LinearRegression().fit(X, y)
    y_hat = m.predict(X)
    resid = y - y_hat
    return {
        "model": m,
        "cols": cols,
        "n": len(d),
        "resid_std": float(np.std(resid, ddof=1)),
        "r2": float(m.score(X, y)),
        "coefs": dict(zip(cols, m.coef_)),
        "intercept": float(m.intercept_),
    }


def report():
    df = load_features()

    # ---- ADP-only bridge (post-COVID)
    b_pc = fit_adp_bridge(df, post_covid_only=True)
    # ---- ADP-only bridge (2010+, wider)
    b_wide = fit_adp_bridge(df, post_covid_only=False)

    print("=" * 70)
    print("ADP-ONLY BRIDGE EQUATION — NFP_change = a + b*ADP_change")
    print("=" * 70)
    for label, b in [("Post-COVID (2022-06+)", b_pc), ("2010+ (COVID-masked)", b_wide)]:
        print(f"\n{label}:")
        print(f"  alpha (intercept):  {b['alpha']:+.1f} K")
        print(f"  beta (ADP coef):    {b['beta']:+.3f}")
        print(f"  R^2:                {b['r2']:.3f}")
        print(f"  n:                  {b['n']}")
        print(f"  resid std (~ RMSE): {b['resid_std']:.1f} K")

    # Prediction using both bridges
    row = df.loc[pd.Timestamp("2026-07-01")]
    adp_jul = row["adp_chg_k"]
    if pd.isna(adp_jul):
        adp_jul = 68.0  # manual override for scenario check
    print(f"\n--- Prediction with ADP_chg_July = {adp_jul:.1f} K ---")
    pred_pc = b_pc["alpha"] + b_pc["beta"] * adp_jul
    pred_wide = b_wide["alpha"] + b_wide["beta"] * adp_jul
    print(f"  ADP-bridge (post-COVID):  {pred_pc:+.1f} K  (RMSE {b_pc['resid_std']:.0f}K)")
    print(f"  ADP-bridge (2010+):       {pred_wide:+.1f} K  (RMSE {b_wide['resid_std']:.0f}K)")

    # Multi-var bridge
    mb = fit_multibridge(df, post_covid_only=True)
    print(f"\n--- MULTI-VAR BRIDGE (ADP + claims + Empire + Philly) ---")
    print(f"  R^2 = {mb['r2']:.3f}, n = {mb['n']}, resid_std = {mb['resid_std']:.1f} K")
    print(f"  Coefficients:")
    for k, v in mb["coefs"].items():
        print(f"    {k:20s} {v:+.4f}")
    print(f"    intercept            {mb['intercept']:+.1f}")
    # Predict for row (fill in missing with reasonable)
    xrow = np.array([[
        adp_jul,
        row["icsa_monthly_mean"] if pd.notna(row["icsa_monthly_mean"]) else 210000,
        row["ccsa_monthly_mean"] if pd.notna(row["ccsa_monthly_mean"]) else 1800000,
        row["empire_emp"] if pd.notna(row["empire_emp"]) else 5.0,
        row["philly_emp"] if pd.notna(row["philly_emp"]) else 5.0,
    ]])
    pred_mb = mb["model"].predict(xrow)[0]
    print(f"  Prediction: {pred_mb:+.1f} K")

    # Save
    out = pd.DataFrame([
        {"model": "ADP-bridge (post-COVID)", "prediction_k": pred_pc, "rmse": b_pc["resid_std"], "n": b_pc["n"]},
        {"model": "ADP-bridge (2010+)", "prediction_k": pred_wide, "rmse": b_wide["resid_std"], "n": b_wide["n"]},
        {"model": "Multi-bridge (5-var)", "prediction_k": pred_mb, "rmse": mb["resid_std"], "n": mb["n"]},
    ])
    out.to_csv(PROC / "bridge_predictions.csv", index=False)
    return out


if __name__ == "__main__":
    report()
