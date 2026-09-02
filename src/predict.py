"""One-shot prediction pipeline.

Loads feature matrix, runs all models, builds inverse-MAE-weighted ensemble
using post-COVID backtest performance, outputs prediction + honest uncertainty.
"""
from __future__ import annotations

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd

from src.build_features import build_feature_matrix, PREDICTION_MONTH
from src.models import predict_next

PROC = Path(__file__).resolve().parent.parent / "data" / "processed"
REPORTS = Path(__file__).resolve().parent.parent / "reports"
REPORTS.mkdir(parents=True, exist_ok=True)

# Manual overrides for late-arriving data (populate as they release)
# Real values as of 2026-08-05 afternoon ET:
#   UMich July final (released 2026-07-31): 55.2 (up from 49.5, 5-month high)
#   ADP July 2026 (released 2026-08-05 08:15 ET): +68K vs 98K consensus (DEEP MISS)
#     Prior June: +98K (level 132722K, so July level ~ 132790K)
MANUAL_OVERRIDES: dict[str, float] = {
    "umcsent": 55.2,
    "adp_chg_k": 44.0,        # ADP July: +44K actual (vs 68K forecast) — CONFIRMED
    "adp_level_k": 132766.0,  # revised-June-level + July +44
}

# Market benchmarks (from professional survey — Bloomberg/Reuters median)
# Note: 120K was pre-set BEFORE today's ADP miss. Post-ADP whisper likely 90-100K.
# Keeping published median; model's downside signal will pull blend slightly.
CONSENSUS_NFP_K = 120.0
CONSENSUS_MAE_HIST_K = 55.0  # historical MAE of consensus vs actual (approx)

# External signals not yet in feature matrix (for narrative context):
#   ISM Mfg Employment Jul: 52.8 (up +3.1 from 49.7, expansion first time in 33mo) - BULLISH
#   ISM Services Employment Jul: not yet indexed (Jun was 51.2)
#   Challenger Job Cuts Jul: 62,075 (+29% MoM, +140% YoY) - BEARISH
#   Dallas Fed Employment: 12.2 (down 2 from Jun) - MILD BULLISH
#   Richmond Fed Employment: 2 (up from -1) - MILD BULLISH
#   KC Fed Employment: positive - MILD BULLISH


def apply_overrides(df: pd.DataFrame, prediction_month: pd.Timestamp,
                    overrides: dict) -> pd.DataFrame:
    if not overrides:
        return df
    df = df.copy()
    for col, val in overrides.items():
        if col in df.columns:
            print(f"[override] {col} at {prediction_month.date()}: {df.at[prediction_month, col]} -> {val}")
            df.at[prediction_month, col] = val
        else:
            print(f"[warn] override column '{col}' not in feature matrix")
    return df


def build_ensemble(preds: pd.DataFrame, summary: pd.DataFrame,
                   exclude: list[str] | None = None) -> dict:
    """Inverse-MAE weighted ensemble across models."""
    exclude = exclude or ["Naive: last value"]
    m = preds.merge(summary[["model", "MAE", "RMSE"]], on="model")
    m = m[~m["model"].isin(exclude)].copy()
    m["weight"] = 1.0 / m["MAE"]
    m["weight"] /= m["weight"].sum()
    m["contribution"] = m["prediction_k"] * m["weight"]

    point = m["contribution"].sum()
    # Two uncertainty measures
    weighted_rmse = np.sqrt((m["weight"] * m["RMSE"] ** 2).sum())
    pred_std = m["prediction_k"].std()  # cross-model dispersion

    return {
        "point_estimate_k": point,
        "weighted_rmse_k": weighted_rmse,
        "model_dispersion_k": pred_std,
        "n_models": len(m),
        "detail": m[["model", "prediction_k", "MAE", "weight", "contribution"]].sort_values("weight", ascending=False),
    }


def run():
    print("=" * 70)
    print(f"NFP FORECAST PIPELINE — target: {PREDICTION_MONTH.date()} (release Fri Aug 7 2026)")
    print("=" * 70)

    # 1. Rebuild features (uses cached FRED CSVs)
    df = build_feature_matrix()
    df.to_csv(PROC / "features.csv")

    # 2. Apply manual overrides for late-breaking data
    df = apply_overrides(df, PREDICTION_MONTH, MANUAL_OVERRIDES)

    # 3. Run all models
    preds = predict_next(df, PREDICTION_MONTH, train_start=pd.Timestamp("2010-01-01"))
    print(f"\n--- Individual model predictions ---")
    print(preds.sort_values("prediction_k").to_string(index=False))

    # 4. Load post-COVID backtest summary + build ensemble
    summary_pc = pd.read_csv(PROC / "backtest_summary_postcovid.csv")
    print(f"\n--- Post-COVID backtest MAE ranking ---")
    print(summary_pc[["model", "MAE", "RMSE", "sign_hit"]].to_string(index=False))

    ens = build_ensemble(preds, summary_pc)
    print(f"\n--- Ensemble contributions ---")
    print(ens["detail"].to_string(index=False))

    # 5. Bayesian blend with market consensus (inverse-variance weighting)
    # Weight = 1/MAE^2 (inverse variance approx). Consensus historical MAE ~55K vs
    # our ensemble weighted RMSE. Combine as w_c * consensus + w_m * model.
    var_c = CONSENSUS_MAE_HIST_K ** 2
    var_m = ens["weighted_rmse_k"] ** 2
    w_c = (1 / var_c) / (1 / var_c + 1 / var_m)
    w_m = 1 - w_c
    blended = w_c * CONSENSUS_NFP_K + w_m * ens["point_estimate_k"]
    blended_rmse = np.sqrt(1 / (1 / var_c + 1 / var_m))

    # 6. Report
    print("\n" + "=" * 70)
    print("FINAL FORECAST — U.S. Nonfarm Payrolls, July 2026")
    print("=" * 70)
    print(f"  Model ensemble:          {ens['point_estimate_k']:+.0f} K jobs")
    print(f"    weighted RMSE:         +/- {ens['weighted_rmse_k']:.0f} K")
    print(f"    cross-model dispersion:+/- {ens['model_dispersion_k']:.0f} K")
    print(f"    n models:              {ens['n_models']}")
    print(f"  Market consensus:        {CONSENSUS_NFP_K:+.0f} K (Bloomberg/Reuters median)")
    print(f"    historical MAE:        +/- {CONSENSUS_MAE_HIST_K:.0f} K")
    print(f"  ----------------------------------------")
    print(f"  BLENDED FORECAST:        {blended:+.0f} K jobs")
    print(f"    weights: consensus {w_c*100:.0f}% + model {w_m*100:.0f}%")
    print(f"    combined RMSE:         +/- {blended_rmse:.0f} K")
    print(f"    ~68% CI: [{blended-blended_rmse:+.0f}, {blended+blended_rmse:+.0f}]")
    print(f"    ~95% CI: [{blended-2*blended_rmse:+.0f}, {blended+2*blended_rmse:+.0f}]")
    print(f"  ----------------------------------------")
    lean = "BELOW" if blended < CONSENSUS_NFP_K - 5 else "ABOVE" if blended > CONSENSUS_NFP_K + 5 else "IN LINE WITH"
    print(f"  DIRECTIONAL LEAN vs consensus: {lean}  ({blended - CONSENSUS_NFP_K:+.0f} K)")

    # 7. Save report
    report_path = REPORTS / f"forecast_{PREDICTION_MONTH.strftime('%Y_%m')}.txt"
    with open(report_path, "w") as f:
        f.write(f"NFP Forecast for reference month {PREDICTION_MONTH.date()}\n")
        f.write(f"Release date: 2026-08-07 08:30 ET\n")
        f.write(f"Generated: {pd.Timestamp.now().isoformat(timespec='seconds')}\n\n")
        f.write(f"BLENDED FORECAST: {blended:+.0f} K jobs\n")
        f.write(f"  weights: consensus {w_c*100:.0f}% + model {w_m*100:.0f}%\n")
        f.write(f"  combined RMSE: {blended_rmse:.0f} K\n")
        f.write(f"  ~68% CI: [{blended-blended_rmse:+.0f}, {blended+blended_rmse:+.0f}]\n")
        f.write(f"  ~95% CI: [{blended-2*blended_rmse:+.0f}, {blended+2*blended_rmse:+.0f}]\n\n")
        f.write(f"Model ensemble: {ens['point_estimate_k']:+.0f} K  (RMSE {ens['weighted_rmse_k']:.0f}K)\n")
        f.write(f"Market consensus: {CONSENSUS_NFP_K:+.0f} K\n\n")
        f.write(f"MANUAL OVERRIDES APPLIED:\n{MANUAL_OVERRIDES}\n\n")
        f.write(f"Individual model predictions:\n")
        f.write(preds.sort_values("prediction_k").to_string(index=False))
        f.write(f"\n\nEnsemble contributions:\n")
        f.write(ens["detail"].to_string(index=False))
    print(f"\nReport saved: {report_path}")

    return {"blended": blended, "blended_rmse": blended_rmse,
            "ensemble": ens, "consensus": CONSENSUS_NFP_K}


if __name__ == "__main__":
    run()
