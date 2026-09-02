"""Walk-forward backtest of bridge equation models."""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))



import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from src.models import load_features, mask_covid

PROC = Path(__file__).resolve().parent.parent / "data" / "processed"


BRIDGE_SPECS = {
    "b_adp_only":        ["adp_chg_k"],
    "b_adp_claims":      ["adp_chg_k", "ic4w_monthly_mean"],
    "b_adp_claims_emp":  ["adp_chg_k", "ic4w_monthly_mean", "empire_emp", "philly_emp"],
    "b_5var":            ["adp_chg_k", "icsa_monthly_mean", "ccsa_monthly_mean", "empire_emp", "philly_emp"],
    "b_ar_ext":          ["adp_chg_k", "nfp_chg_lag1", "ic4w_monthly_mean", "empire_emp", "philly_emp"],
    "b_ar":              ["nfp_chg_lag1", "nfp_chg_3m_avg"],
    "b_adp_ar":          ["adp_chg_k", "nfp_chg_lag1", "nfp_chg_3m_avg"],
    "b_kitchen":         ["adp_chg_k", "ic4w_monthly_mean", "empire_emp", "philly_emp",
                          "nfp_chg_lag1", "nfp_chg_3m_avg", "umcsent", "y10_m"],
    # NEW: ref-week claims and ISM Employment bridges
    "b_refwk_only":      ["icsa_ref_week"],
    "b_refwk_adp":       ["icsa_ref_week", "adp_chg_k"],
    "b_refwk_ism":       ["icsa_ref_week", "ism_mfg_emp"],
    "b_ism_adp":         ["ism_mfg_emp", "adp_chg_k"],
    "b_leading_5":       ["icsa_ref_week", "adp_chg_k", "ism_mfg_emp", "empire_emp", "philly_emp"],
    "b_supertight":      ["icsa_ref_week", "adp_chg_k", "ism_mfg_emp"],
    # Vintage-aware JOLTS bridges (uses first-print JOLTS, not revised)
    "b_vintage_jolts":   ["adp_chg_k", "icsa_ref_week", "jolts_openings_fp"],
    "b_vintage_full":    ["adp_chg_k", "icsa_ref_week", "jolts_openings_fp", "empire_emp", "philly_emp"],
}


def walk_forward_bridge(df: pd.DataFrame, cols: list[str],
                        test_start=pd.Timestamp("2015-01-01"),
                        test_end=pd.Timestamp("2026-06-01"),
                        min_train=48,
                        post_covid_only=False):
    """COVID-mask applied to BOTH training and test (evaluation) to avoid noise."""
    tgt = "target_nfp_chg_k"
    df = df.copy()
    dates = pd.date_range(test_start, test_end, freq="MS")
    # Filter test dates: skip COVID months
    from src.models import COVID_START, COVID_END
    dates = dates[(dates < COVID_START) | (dates > COVID_END)]
    records = []
    for t in dates:
        train = df[df.index < t]
        train = mask_covid(train)
        train = train.dropna(subset=[tgt] + cols)
        if post_covid_only:
            train = train[train.index >= pd.Timestamp("2022-06-01")]
        if len(train) < min_train:
            continue
        if t not in df.index:
            continue
        test = df.loc[[t], cols + [tgt]].copy()
        if test[cols].isna().any(axis=1).iloc[0] or pd.isna(test[tgt].iloc[0]):
            continue
        m = LinearRegression().fit(train[cols].values, train[tgt].values)
        pred = m.predict(test[cols].values)[0]
        actual = test[tgt].iloc[0]
        records.append({"date": t, "pred": pred, "actual": actual, "n_train": len(train)})
    if len(records) == 0:
        return pd.DataFrame(columns=["date", "pred", "actual", "n_train"]).set_index("date")
    return pd.DataFrame(records).set_index("date")


def summarize_bt(bt: pd.DataFrame, name: str) -> dict:
    err = bt["pred"] - bt["actual"]
    return {
        "model": name,
        "n": len(bt),
        "MAE": float(np.mean(np.abs(err))),
        "RMSE": float(np.sqrt(np.mean(err**2))),
        "bias": float(np.mean(err)),
        "sign_hit": float((np.sign(bt["pred"]) == np.sign(bt["actual"])).mean()),
    }


# Manual overrides matching predict.py (for the prediction step below)
# 2026-08-05 confirmed from investing.com after release:
#   ADP July: +44K actual (vs 68K forecast, prev 95K revised from 98K)
JULY_OVERRIDES = {
    "umcsent": 55.2,
    "adp_chg_k": 44.0,
    "adp_level_k": 132766.0,  # revised June (132722 -3 for rev) + July +44
}


def run():
    df = load_features()

    # Apply July overrides for prediction
    for c, v in JULY_OVERRIDES.items():
        if c in df.columns:
            df.at[pd.Timestamp("2026-07-01"), c] = v

    rows = []
    # Both walk-forward regimes: 2015+ with wider training, and 2018+ with narrower window
    print("=" * 70)
    print("BRIDGE MODEL WALK-FORWARD (COVID masked in train & test)")
    print("=" * 70)
    for name, cols in BRIDGE_SPECS.items():
        bt = walk_forward_bridge(df, cols,
                                 test_start=pd.Timestamp("2015-01-01"),
                                 test_end=pd.Timestamp("2026-06-01"),
                                 post_covid_only=False, min_train=48)
        if len(bt) > 5:
            rows.append(summarize_bt(bt, name))
    summary = pd.DataFrame(rows).sort_values("MAE")
    print(summary.to_string(index=False))
    summary.to_csv(PROC / "bridge_backtest_summary.csv", index=False)

    # Predictions for Jul 2026
    print("\n--- Predictions for Jul 2026 (post-COVID-only training window) ---")
    row_jul = df.loc[pd.Timestamp("2026-07-01")]
    pred_rows = []
    for name, cols in BRIDGE_SPECS.items():
        train = df[df.index < pd.Timestamp("2026-07-01")]
        train = mask_covid(train).dropna(subset=["target_nfp_chg_k"] + cols)
        train_pc = train[train.index >= pd.Timestamp("2022-06-01")]
        if any(pd.isna(row_jul[c]) for c in cols):
            missing = [c for c in cols if pd.isna(row_jul[c])]
            print(f"  {name:20s}  SKIP (missing {missing})")
            continue
        m = LinearRegression().fit(train_pc[cols].values, train_pc["target_nfp_chg_k"].values)
        x = row_jul[cols].values.reshape(1, -1)
        pred = m.predict(x)[0]
        pred_rows.append({"model": name, "prediction_k": float(pred), "cols": ",".join(cols)})
        print(f"  {name:20s}  {pred:+7.1f} K")

    print("\n--- Predictions for Jul 2026 (2010+ COVID-masked training window) ---")
    for name, cols in BRIDGE_SPECS.items():
        train = df[df.index < pd.Timestamp("2026-07-01")]
        train = mask_covid(train).dropna(subset=["target_nfp_chg_k"] + cols)
        train_full = train[train.index >= pd.Timestamp("2010-01-01")]
        if any(pd.isna(row_jul[c]) for c in cols):
            continue
        m = LinearRegression().fit(train_full[cols].values, train_full["target_nfp_chg_k"].values)
        x = row_jul[cols].values.reshape(1, -1)
        pred = m.predict(x)[0]
        pred_rows.append({"model": f"{name}_wide", "prediction_k": float(pred), "cols": ",".join(cols)})
        print(f"  {name+'_wide':25s}  {pred:+7.1f} K")

    preds = pd.DataFrame(pred_rows)
    preds.to_csv(PROC / "bridge_predictions_jul_2026.csv", index=False)
    return summary, preds


if __name__ == "__main__":
    run()
