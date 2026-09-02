"""Stacking meta-learner: use base model out-of-sample predictions as features
to a Ridge meta-learner. Common accuracy boost of 5-10K MAE.

Approach:
  1. For each month t in the training set, compute out-of-fold predictions
     from each base model (trained on data-through-(t-1)).
  2. Fit a Ridge meta-learner on these OOF predictions -> actual target.
  3. For prediction: train base models on all data, generate their predictions,
     feed to fitted meta-learner.
"""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))



import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler

from src.first_print_model import (build_first_print_features, make_models)
from src.models import mask_covid, COVID_START, COVID_END
from src.build_features import PREDICTION_MONTH
from src.bridge_backtest import JULY_OVERRIDES

PROC = Path(__file__).resolve().parent.parent / "data" / "processed"


def stack_walk_forward(df, target_col, feature_cols,
                       train_start=pd.Timestamp("2010-01-01"),
                       stack_start=pd.Timestamp("2020-06-01"),
                       stack_end=pd.Timestamp("2026-06-01"),
                       min_train=48):
    """Walk-forward to produce out-of-fold predictions for the stacker.
    Returns DataFrame of (date, actual, base_pred_1, base_pred_2, ...)."""
    dates = pd.date_range(stack_start, stack_end, freq="MS")
    dates = dates[(dates < COVID_START) | (dates > COVID_END)]

    base_models = make_models()
    records = []
    for t in dates:
        train = df[(df.index >= train_start) & (df.index < t)]
        train = mask_covid(train).dropna(subset=[target_col] + feature_cols)
        if len(train) < min_train:
            continue
        if t not in df.index or pd.isna(df.at[t, target_col]):
            continue
        row = df.loc[[t]]
        if row[feature_cols].isna().any(axis=1).iloc[0]:
            continue
        X_tr = train[feature_cols].values
        y_tr = train[target_col].values
        X_te = row[feature_cols].values

        rec = {"date": t, "actual": row[target_col].iloc[0]}
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        X_te_s = scaler.transform(X_te)
        for name, m in base_models:
            m.fit(X_tr_s, y_tr)
            rec[name] = float(m.predict(X_te_s)[0])
        records.append(rec)
    return pd.DataFrame(records).set_index("date")


def fit_stacker(oof: pd.DataFrame, meta_alpha: float = 1.0):
    """Fit Ridge meta-learner on base OOF predictions."""
    base_cols = [c for c in oof.columns if c != "actual"]
    X = oof[base_cols].values
    y = oof["actual"].values
    m = Ridge(alpha=meta_alpha, positive=False).fit(X, y)  # allow negative weights
    return m, base_cols


def predict_with_stack(df_new_row, target_col, feature_cols, train_full, meta_model, base_cols):
    """Given feature row, generate base preds then meta prediction."""
    X_tr = train_full[feature_cols].values
    y_tr = train_full[target_col].values
    scaler = StandardScaler().fit(X_tr)
    X_tr_s = scaler.transform(X_tr)
    X_te_s = scaler.transform(df_new_row[feature_cols].values)

    base_preds = {}
    for name, m in make_models():
        m.fit(X_tr_s, y_tr)
        base_preds[name] = float(m.predict(X_te_s)[0])
    stack_X = np.array([[base_preds[c] for c in base_cols]])
    meta_pred = float(meta_model.predict(stack_X)[0])
    return meta_pred, base_preds


def run():
    print("=" * 70)
    print("STACKING META-LEARNER — first-print target")
    print("=" * 70)

    df = build_first_print_features()
    target_col = "target_first_print_k"
    exclude = {"target_nfp_chg_k", "nfp_chg_lag1", "nfp_chg_lag2", "nfp_chg_lag3",
               "nfp_chg_3m_avg", "nfp_chg_6m_avg", "nfp_chg_12m_avg"}
    feature_cols = [c for c in df.columns if c not in exclude and c != target_col]

    # 1. Generate OOF base predictions
    print("Generating out-of-fold predictions...")
    oof = stack_walk_forward(df, target_col, feature_cols,
                             train_start=pd.Timestamp("2010-01-01"),
                             stack_start=pd.Timestamp("2018-01-01"),
                             stack_end=pd.Timestamp("2026-06-01"))
    print(f"OOF sample size: {len(oof)}")
    print(f"OOF columns: {oof.columns.tolist()}")

    # 2. Fit meta-learner (train on pre-2024, test on 2024-2026)
    train_oof = oof[oof.index < "2024-01-01"]
    test_oof = oof[oof.index >= "2024-01-01"]
    print(f"\nMeta-train sample: {len(train_oof)}, meta-test sample: {len(test_oof)}")

    best = None
    for alpha in [0.5, 1.0, 5.0, 10.0, 50.0]:
        meta, base_cols = fit_stacker(train_oof, meta_alpha=alpha)
        test_preds = meta.predict(test_oof[base_cols].values)
        test_actual = test_oof["actual"].values
        mae = np.mean(np.abs(test_preds - test_actual))
        rmse = np.sqrt(np.mean((test_preds - test_actual) ** 2))
        print(f"  alpha={alpha:6.1f}  MAE={mae:6.1f}  RMSE={rmse:6.1f}  "
              f"weights: {dict(zip(base_cols, np.round(meta.coef_, 2)))}")
        if best is None or mae < best["mae"]:
            best = {"alpha": alpha, "mae": mae, "rmse": rmse, "meta": meta, "base_cols": base_cols}

    print(f"\nBest alpha: {best['alpha']} with MAE {best['mae']:.1f}K RMSE {best['rmse']:.1f}K")

    # 3. Compare meta vs simple mean of base models
    simple_mean = test_oof[best["base_cols"]].mean(axis=1)
    simple_mae = np.mean(np.abs(simple_mean.values - test_oof["actual"].values))
    print(f"  vs simple base-mean MAE: {simple_mae:.1f}K")

    # 4. Refit meta on all OOF, predict July 2026
    # First apply overrides
    for c, v in JULY_OVERRIDES.items():
        if c in df.columns:
            df.at[PREDICTION_MONTH, c] = v
    train_full = df[(df.index >= pd.Timestamp("2010-01-01")) & (df.index < PREDICTION_MONTH)]
    train_full = mask_covid(train_full).dropna(subset=[target_col] + feature_cols)
    # Handle missing features in prediction row (impute)
    row = df.loc[[PREDICTION_MONTH], feature_cols].copy()
    missing = row.columns[row.isna().any()].tolist()
    for c in missing:
        row[c] = train_full[c].iloc[-1]

    meta_full, base_cols = fit_stacker(oof, meta_alpha=best["alpha"])
    meta_pred, base_preds = predict_with_stack(row, target_col, feature_cols,
                                                train_full, meta_full, base_cols)

    print(f"\n--- STACKED FIRST-PRINT PREDICTION for JUL 2026 ---")
    print(f"  Base predictions:")
    for c, v in base_preds.items():
        print(f"    {c:15s} {v:+7.1f} K")
    print(f"\n  META (Ridge alpha={best['alpha']}) prediction: {meta_pred:+7.1f} K")
    print(f"  Meta-learner OOS MAE on 2024-2026 holdout: {best['mae']:.1f}K")

    # Save
    out = {"stack_meta_pred_k": meta_pred, "meta_alpha": best["alpha"],
           "meta_mae_oos": best["mae"], "meta_rmse_oos": best["rmse"]}
    pd.DataFrame([out]).to_csv(PROC / "stacked_prediction.csv", index=False)
    return meta_pred, best


if __name__ == "__main__":
    run()
