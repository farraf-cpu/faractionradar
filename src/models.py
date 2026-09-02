"""Model bakeoff for NFP MoM-change prediction with walk-forward backtest.

Models:
  - Naive: last value
  - Naive: 3-month rolling mean
  - Naive: 12-month rolling mean
  - OLS baseline (top-k features by correlation)
  - Ridge
  - Elastic Net
  - Random Forest
  - Gradient Boosting (sklearn)
  - XGBoost

COVID handling: mask 2020-04 to 2020-12 from BOTH training and evaluation.
The pandemic distortion (-20M April) would dominate any regression fit.
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNetCV, Ridge, LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

PROC = Path(__file__).resolve().parent.parent / "data" / "processed"
COVID_START = pd.Timestamp("2020-03-01")
COVID_END = pd.Timestamp("2020-12-01")


def load_features() -> pd.DataFrame:
    df = pd.read_csv(PROC / "features.csv", parse_dates=["date"], index_col="date")
    return df


def mask_covid(df: pd.DataFrame) -> pd.DataFrame:
    m = (df.index >= COVID_START) & (df.index <= COVID_END)
    return df[~m]


class NaiveLast:
    name = "Naive: last value"
    def fit(self, X, y): self.last_ = y.iloc[-1]; return self
    def predict(self, X): return np.full(len(X), self.last_)


class NaiveRolling:
    def __init__(self, w=3): self.w = w; self.name = f"Naive: {w}m avg"
    def fit(self, X, y): self.mean_ = y.tail(self.w).mean(); return self
    def predict(self, X): return np.full(len(X), self.mean_)


class ScaledModel:
    """Wraps any sklearn regressor with a StandardScaler on X."""
    def __init__(self, model, name):
        self.model = model
        self.scaler = StandardScaler()
        self.name = name

    def fit(self, X, y):
        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs, y)
        return self

    def predict(self, X):
        Xs = self.scaler.transform(X)
        return self.model.predict(Xs)


def make_models():
    return [
        NaiveLast(),
        NaiveRolling(3),
        NaiveRolling(12),
        ScaledModel(LinearRegression(), "OLS"),
        ScaledModel(Ridge(alpha=1.0), "Ridge(1.0)"),
        ScaledModel(Ridge(alpha=10.0), "Ridge(10)"),
        ScaledModel(ElasticNetCV(cv=5, max_iter=20000, l1_ratio=[0.1, 0.5, 0.9]), "ElasticNetCV"),
        ScaledModel(RandomForestRegressor(n_estimators=300, max_depth=6, random_state=42, n_jobs=-1), "RF(300,d6)"),
        ScaledModel(GradientBoostingRegressor(n_estimators=200, max_depth=3, learning_rate=0.05, random_state=42), "GBM(200,d3)"),
    ]

# XGBoost added conditionally
try:
    from xgboost import XGBRegressor
    def xgb_model():
        return ScaledModel(
            XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                         subsample=0.8, colsample_bytree=0.8, random_state=42,
                         verbosity=0, n_jobs=-1),
            "XGB(300,d4)")
except ImportError:
    xgb_model = None


def walk_forward_backtest(
    df: pd.DataFrame,
    train_start: pd.Timestamp,
    test_start: pd.Timestamp,
    test_end: pd.Timestamp,
    min_train_months: int = 60,
) -> pd.DataFrame:
    """For each month in [test_start, test_end], train on data through (test_month - 1)
    and predict test_month. Return per-model predictions + errors."""
    target_col = "target_nfp_chg_k"
    feature_cols = [c for c in df.columns if c != target_col]

    df = df[df.index >= train_start].copy()

    # complete cases only for X + y in the training data
    def prep(sub):
        sub = mask_covid(sub)
        sub = sub.dropna(subset=[target_col] + feature_cols)
        return sub

    test_months = pd.date_range(test_start, test_end, freq="MS")

    all_models = make_models()
    if xgb_model is not None:
        all_models.append(xgb_model())

    records = []
    for t in test_months:
        train_slice = df[df.index < t]
        train_clean = prep(train_slice)
        if len(train_clean) < min_train_months:
            continue

        # Test row must have all features non-null AND target present
        if t not in df.index:
            continue
        test_row = df.loc[[t]]
        if test_row[feature_cols].isna().any(axis=1).iloc[0]:
            continue
        if pd.isna(test_row[target_col].iloc[0]):
            continue

        X_train = train_clean[feature_cols].values
        y_train = train_clean[target_col].values
        X_test = test_row[feature_cols].values
        y_test = test_row[target_col].values[0]

        rec = {"date": t, "actual": y_test, "n_train": len(train_clean)}
        for m in all_models:
            m.fit(pd.DataFrame(X_train, columns=feature_cols),
                  pd.Series(y_train))
            pred = m.predict(pd.DataFrame(X_test, columns=feature_cols))[0]
            rec[m.name] = pred
        records.append(rec)

    return pd.DataFrame(records).set_index("date")


def summarize(bt: pd.DataFrame) -> pd.DataFrame:
    """Compute RMSE, MAE, sign-hit-rate for each model column vs actual."""
    actual = bt["actual"]
    model_cols = [c for c in bt.columns if c not in ("actual", "n_train")]
    rows = []
    for c in model_cols:
        pred = bt[c]
        err = pred - actual
        rmse = np.sqrt(np.mean(err**2))
        mae = np.mean(np.abs(err))
        # Sign hit-rate (up vs down, using sign of actual and pred deviation from 0)
        sign_hit = (np.sign(pred) == np.sign(actual)).mean()
        rows.append({"model": c, "RMSE": rmse, "MAE": mae, "sign_hit": sign_hit,
                     "bias": err.mean()})
    return pd.DataFrame(rows).sort_values("MAE")


def predict_next(df: pd.DataFrame, prediction_month: pd.Timestamp,
                 train_start: pd.Timestamp = pd.Timestamp("2010-01-01")) -> pd.DataFrame:
    """Train each model on all-available-data-up-to-prediction-month, predict that month."""
    target_col = "target_nfp_chg_k"
    feature_cols = [c for c in df.columns if c != target_col]

    train = df[(df.index >= train_start) & (df.index < prediction_month)]
    train = mask_covid(train)
    train = train.dropna(subset=[target_col] + feature_cols)

    if prediction_month not in df.index:
        raise ValueError(f"No row for {prediction_month}")
    pred_row = df.loc[[prediction_month], feature_cols]
    missing = pred_row.columns[pred_row.isna().any()].tolist()
    if missing:
        # Impute with last-available value from training
        for c in missing:
            pred_row[c] = train[c].iloc[-1]
        print(f"[predict_next] Imputed {len(missing)} missing features with last-known:")
        for c in missing:
            print(f"    {c} -> {pred_row[c].iloc[0]:.3f}")

    X_train = train[feature_cols].values
    y_train = train[target_col].values
    X_test = pred_row.values

    all_models = make_models()
    if xgb_model is not None:
        all_models.append(xgb_model())

    rows = []
    for m in all_models:
        m.fit(pd.DataFrame(X_train, columns=feature_cols), pd.Series(y_train))
        pred = m.predict(pd.DataFrame(X_test, columns=feature_cols))[0]
        rows.append({"model": m.name, "prediction_k": pred})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = load_features()
    print(f"Loaded features: {df.shape}\n")

    print("=" * 70)
    print("WALK-FORWARD BACKTEST: 2015-01 -> 2026-06 (excl COVID mask)")
    print("=" * 70)
    bt = walk_forward_backtest(
        df,
        train_start=pd.Timestamp("2005-01-01"),
        test_start=pd.Timestamp("2015-01-01"),
        test_end=pd.Timestamp("2026-06-01"),
    )
    print(f"Backtest windows evaluated: {len(bt)}")
    summary = summarize(bt)
    print("\nBacktest summary (sorted by MAE, all values in thousands):")
    print(summary.to_string(index=False))

    # Save
    bt.to_csv(PROC / "backtest_results.csv")
    summary.to_csv(PROC / "backtest_summary.csv", index=False)

    print("\n" + "=" * 70)
    print("POST-COVID BACKTEST: 2022-06 -> 2026-06 (recent regime)")
    print("=" * 70)
    bt_pc = walk_forward_backtest(
        df,
        train_start=pd.Timestamp("2010-01-01"),
        test_start=pd.Timestamp("2022-06-01"),
        test_end=pd.Timestamp("2026-06-01"),
    )
    print(f"Backtest windows evaluated: {len(bt_pc)}")
    summary_pc = summarize(bt_pc)
    print("\nPost-COVID summary:")
    print(summary_pc.to_string(index=False))
    summary_pc.to_csv(PROC / "backtest_summary_postcovid.csv", index=False)

    print("\n" + "=" * 70)
    print(f"PREDICTION FOR JUL 2026 (release Fri Aug 7)")
    print("=" * 70)
    preds = predict_next(df, pd.Timestamp("2026-07-01"),
                         train_start=pd.Timestamp("2010-01-01"))
    preds = preds.sort_values("prediction_k")
    print(preds.to_string(index=False))
    print(f"\nMean of top-3 (by post-COVID MAE): "
          f"{preds.merge(summary_pc[['model','MAE']]).nsmallest(3,'MAE')['prediction_k'].mean():.1f}K")
    preds.to_csv(PROC / "predictions_jul_2026.csv", index=False)
