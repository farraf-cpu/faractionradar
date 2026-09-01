"""Sensitivity table: how much does the forecast change with each input?

Rerun the model stack multiple times with alternative values for key inputs
to bound the range of reasonable forecasts.
"""
from __future__ import annotations

import sys
sys.path.insert(0, "C:/Predictor")

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.build_features import build_feature_matrix, PREDICTION_MONTH
from src.models import mask_covid
from src.bridge_backtest import BRIDGE_SPECS, JULY_OVERRIDES

PROC = Path("C:/Predictor/data/processed")


def run_scenario(overrides: dict) -> dict:
    """Compute a lightweight blended forecast given overrides."""
    df = build_feature_matrix()
    for c, v in overrides.items():
        if c in df.columns:
            df.at[PREDICTION_MONTH, c] = v

    # Run each bridge
    row = df.loc[PREDICTION_MONTH]
    train = df[df.index < PREDICTION_MONTH]
    train = mask_covid(train)

    preds = []
    for name, cols in BRIDGE_SPECS.items():
        for win in [pd.Timestamp("2022-06-01"), pd.Timestamp("2010-01-01")]:
            t = train[train.index >= win].dropna(subset=["target_nfp_chg_k"] + cols)
            if any(pd.isna(row[c]) for c in cols) or len(t) < 30:
                continue
            m = LinearRegression().fit(t[cols].values, t["target_nfp_chg_k"].values)
            pred = float(m.predict(row[cols].values.reshape(1, -1))[0])
            preds.append(pred)

    return {
        "median": float(np.median(preds)),
        "mean": float(np.mean(preds)),
        "n": len(preds),
    }


def sensitivity_table():
    scenarios = []

    # Baseline
    base = JULY_OVERRIDES.copy()
    scenarios.append(("BASELINE (ADP 44, UMich 55.2)", base))

    # ADP scenarios
    for adp in [30, 44, 60, 80, 100]:
        s = base.copy()
        s["adp_chg_k"] = adp
        s["adp_level_k"] = 132722 + adp
        scenarios.append((f"ADP = {adp}K", s))

    # UMich scenarios
    for umich in [50, 55.2, 60, 65]:
        s = base.copy()
        s["umcsent"] = umich
        scenarios.append((f"UMich = {umich}", s))

    print("=" * 78)
    print("SENSITIVITY: how much does the median bridge forecast change?")
    print("=" * 78)
    print(f"\n{'Scenario':40s}  {'Bridge median':>15s}  {'Bridge mean':>12s}")
    print("-" * 78)
    for label, ovr in scenarios:
        result = run_scenario(ovr)
        print(f"{label:40s}  {result['median']:+13.1f} K  {result['mean']:+10.1f} K")


if __name__ == "__main__":
    sensitivity_table()
