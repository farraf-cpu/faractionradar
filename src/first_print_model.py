"""Train models to predict FIRST-PRINT NFP (what will be reported on release day),
not revised. Uses ALFRED-fetched first-print history as target.

This corrects the systematic bias where post-COVID first-prints are ~27-43K higher
than the eventual revised values. Consensus (Bloomberg) predicts first-prints, so
matching that target lets us compare apples-to-apples.
"""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))



import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, ElasticNetCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler

from src.build_features import build_feature_matrix, PREDICTION_MONTH
from src.models import mask_covid
from src.bridge_backtest import JULY_OVERRIDES
try:
    from xgboost import XGBRegressor
except ImportError:
    XGBRegressor = None

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
PROC = Path(__file__).resolve().parent.parent / "data" / "processed"


def load_first_print_target() -> pd.Series:
    """Return first-print NFP change (reported on release day), indexed by ref_month."""
    fp = pd.read_csv(RAW / "PAYEMS_FIRST_PRINT.csv", parse_dates=["ref_month"])
    fp = fp.sort_values("ref_month")
    s = fp.set_index("ref_month")["reported_change_k"]
    s.index = s.index.to_period("M").to_timestamp()
    return s


def build_first_print_features() -> pd.DataFrame:
    """Feature matrix with first-print target replacing revised target."""
    df = build_feature_matrix()
    # Apply July overrides (real data landed today)
    for c, v in JULY_OVERRIDES.items():
        if c in df.columns:
            df.at[PREDICTION_MONTH, c] = v
    fp_target = load_first_print_target()
    df["target_first_print_k"] = fp_target.reindex(df.index)
    # Also add first-print AR lags — first-print autoregressive features are more
    # informative for predicting first-prints than revised lags
    df["fp_chg_lag1"] = fp_target.shift(1).reindex(df.index)
    df["fp_chg_lag2"] = fp_target.shift(2).reindex(df.index)
    df["fp_chg_3m_avg"] = fp_target.shift(1).rolling(3).mean().reindex(df.index)
    df["fp_chg_6m_avg"] = fp_target.shift(1).rolling(6).mean().reindex(df.index)
    return df


def make_models():
    models = [
        ("Ridge(1.0)", Ridge(alpha=1.0)),
        ("Ridge(10)", Ridge(alpha=10.0)),
        ("Ridge(50)", Ridge(alpha=50.0)),
        ("ElasticNetCV", ElasticNetCV(cv=5, max_iter=20000, l1_ratio=[0.1, 0.5, 0.9])),
        ("RF(300,d6)", RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42, n_jobs=-1)),
        ("GBM(200,d3)", GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42)),
    ]
    if XGBRegressor is not None:
        models.append(("XGB(300,d4)",
                       XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                                    subsample=0.8, colsample_bytree=0.8, random_state=42,
                                    verbosity=0, n_jobs=-1)))
    return models


def walk_forward(df, target_col, feature_cols, train_start, test_start, test_end, min_train=60):
    from src.models import COVID_START, COVID_END
    dates = pd.date_range(test_start, test_end, freq="MS")
    dates = dates[(dates < COVID_START) | (dates > COVID_END)]

    all_records = []
    models = make_models()
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
        y_te = row[target_col].iloc[0]

        rec = {"date": t, "actual": y_te}
        scaler = StandardScaler().fit(X_tr)
        X_tr_s = scaler.transform(X_tr)
        X_te_s = scaler.transform(X_te)
        for name, m in models:
            m.fit(X_tr_s, y_tr)
            rec[name] = float(m.predict(X_te_s)[0])
        all_records.append(rec)
    return pd.DataFrame(all_records).set_index("date")


def summarize(bt):
    actual = bt["actual"]
    rows = []
    for c in bt.columns:
        if c == "actual":
            continue
        err = bt[c] - actual
        rows.append({
            "model": c,
            "n": len(bt),
            "MAE": float(np.mean(np.abs(err))),
            "RMSE": float(np.sqrt(np.mean(err**2))),
            "bias": float(err.mean()),
            "sign_hit": float((np.sign(bt[c]) == np.sign(actual)).mean()),
        })
    return pd.DataFrame(rows).sort_values("MAE")


def predict_first_print(df, prediction_month, target_col, feature_cols,
                        train_start=pd.Timestamp("2010-01-01")):
    train = df[(df.index >= train_start) & (df.index < prediction_month)]
    train = mask_covid(train).dropna(subset=[target_col] + feature_cols)
    row = df.loc[[prediction_month], feature_cols].copy()
    missing = row.columns[row.isna().any()].tolist()
    for c in missing:
        row[c] = train[c].iloc[-1]

    X_tr = train[feature_cols].values
    y_tr = train[target_col].values
    scaler = StandardScaler().fit(X_tr)
    X_te = scaler.transform(row.values)
    X_tr_s = scaler.transform(X_tr)

    rows = []
    for name, m in make_models():
        m.fit(X_tr_s, y_tr)
        pred = float(m.predict(X_te)[0])
        rows.append({"model": name, "prediction_k": pred})
    return pd.DataFrame(rows)


def run():
    print("=" * 70)
    print("FIRST-PRINT MODEL — target = reported headline (release-day value)")
    print("=" * 70)

    df = build_first_print_features()

    target_col = "target_first_print_k"
    # Feature set: all original features except revised target + revised AR lags
    exclude = {"target_nfp_chg_k", "nfp_chg_lag1", "nfp_chg_lag2", "nfp_chg_lag3",
               "nfp_chg_3m_avg", "nfp_chg_6m_avg", "nfp_chg_12m_avg"}
    # Also exclude low-history features that would shrink training sample
    # (post-COVID training window has n~50; features with <60 months history hurt)
    MIN_HISTORY_MONTHS = 60
    low_history = {c for c in df.columns
                   if df[c].notna().sum() < MIN_HISTORY_MONTHS}
    if low_history:
        print(f"[filter] Excluding low-history features (<{MIN_HISTORY_MONTHS}mo): {sorted(low_history)}")
    exclude |= low_history
    feature_cols = [c for c in df.columns if c not in exclude and c != target_col]

    # 1. Walk-forward backtest
    print("\n--- Walk-forward: 2015 -> 2026 (COVID masked, first-print target) ---")
    bt = walk_forward(df, target_col, feature_cols,
                      train_start=pd.Timestamp("2005-01-01"),
                      test_start=pd.Timestamp("2015-01-01"),
                      test_end=pd.Timestamp("2026-06-01"),
                      min_train=60)
    summary = summarize(bt)
    print(summary.to_string(index=False))
    summary.to_csv(PROC / "first_print_backtest_summary.csv", index=False)

    # 2. Post-COVID walk-forward
    print("\n--- Walk-forward: 2022-06 -> 2026-06 (post-COVID only test) ---")
    bt_pc = walk_forward(df, target_col, feature_cols,
                         train_start=pd.Timestamp("2010-01-01"),
                         test_start=pd.Timestamp("2022-06-01"),
                         test_end=pd.Timestamp("2026-06-01"),
                         min_train=48)
    summary_pc = summarize(bt_pc)
    print(summary_pc.to_string(index=False))
    summary_pc.to_csv(PROC / "first_print_backtest_summary_postcovid.csv", index=False)

    # 3. Predict July 2026 first-print
    print(f"\n--- July 2026 FIRST-PRINT prediction ---")
    preds = predict_first_print(df, PREDICTION_MONTH, target_col, feature_cols)
    preds = preds.merge(summary_pc[["model", "MAE", "RMSE"]], on="model")
    preds["weight"] = 1.0 / preds["MAE"]
    preds["weight"] /= preds["weight"].sum()
    preds["contribution"] = preds["prediction_k"] * preds["weight"]
    print(preds.to_string(index=False))

    ensemble = float(preds["contribution"].sum())
    ens_rmse = float(np.sqrt((preds["weight"] * preds["RMSE"]**2).sum()))
    ens_dispersion = float(preds["prediction_k"].std())

    print(f"\nFirst-print ensemble: {ensemble:+.1f} K")
    print(f"  weighted RMSE: {ens_rmse:.0f} K")
    print(f"  dispersion: {ens_dispersion:.0f} K")

    # 4. Compare with revised-target prediction (for the same features)
    revised_target = "target_nfp_chg_k"
    revised_bt = walk_forward(df, revised_target, feature_cols,
                              train_start=pd.Timestamp("2010-01-01"),
                              test_start=pd.Timestamp("2022-06-01"),
                              test_end=pd.Timestamp("2026-06-01"),
                              min_train=48)
    revised_summary = summarize(revised_bt)
    print(f"\n--- Revised-target model performance (for comparison) ---")
    print(revised_summary.to_string(index=False))

    preds.to_csv(PROC / "first_print_predictions_jul_2026.csv", index=False)
    return preds, ensemble, ens_rmse


if __name__ == "__main__":
    run()
