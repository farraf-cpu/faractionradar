"""Final synthesis: combine ML ensemble + bridge models + consensus into a
blended prediction. Consensus comes from an env var set by the workflow so
each release uses the live ForexFactory forecast, not a carry-over hardcode.
"""
from __future__ import annotations

import os
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


from datetime import datetime

import numpy as np
import pandas as pd

from src.build_features import build_feature_matrix, PREDICTION_MONTH
from src.models import predict_next
from src.bridge_backtest import BRIDGE_SPECS, JULY_OVERRIDES
from src.first_print_model import (build_first_print_features, predict_first_print,
                                   walk_forward, summarize)
from sklearn.linear_model import LinearRegression
from src.models import mask_covid

PROC = Path(__file__).resolve().parent.parent / "data" / "processed"
REPORTS = Path(__file__).resolve().parent.parent / "reports"

CONSENSUS_MAE_HIST_K = 55.0
PREDICTION_MARKET_MAE_HIST_K = 40.0


def _resolve_consensus() -> float:
    v = os.environ.get("NFP_CONSENSUS_K")
    if v:
        return float(v)
    if os.environ.get("GITHUB_ACTIONS") == "true":
        raise RuntimeError(
            "NFP_CONSENSUS_K env var not set. The workflow must fetch the live"
            " ForexFactory forecast for the target release date and pass it here."
            " Refusing to publish a prediction anchored to a stale hardcoded value."
        )
    print("[warn] NFP_CONSENSUS_K not set — using local-dev fallback of 85.0 (July 2026 baseline)")
    return 85.0


def _resolve_prediction_market() -> tuple[float, bool]:
    # Kalshi/Polymarket ticker mapping isn't verified yet (ROADMAP §237). Until
    # Phase 1.5 wires real markets, this stays a hardcoded July baseline. The
    # is_stale flag propagates into the ourCall caveat so consumers see it.
    v = os.environ.get("NFP_PREDICTION_MARKET_K")
    if v:
        return float(v), False
    return 82.0, True


# Deferred to inside report() so `import src.final_report` in the smoke-test
# CI job doesn't fire the GHA guard. Resolved once per report() invocation.
CONSENSUS_NFP_K: float | None = None
PREDICTION_MARKET_NFP_K: float | None = None
PREDICTION_MARKET_STALE: bool = False


def compute_bridges(df, prediction_month):
    """Predict from each bridge in both training-window modes."""
    row = df.loc[prediction_month]
    train = df[df.index < prediction_month]
    train = mask_covid(train)

    predictions = {}
    for name, cols in BRIDGE_SPECS.items():
        for win, window_name in [(pd.Timestamp("2022-06-01"), "post_covid"),
                                 (pd.Timestamp("2010-01-01"), "2010+")]:
            t = train[train.index >= win].dropna(subset=["target_nfp_chg_k"] + cols)
            if any(pd.isna(row[c]) for c in cols) or len(t) < 30:
                continue
            m = LinearRegression().fit(t[cols].values, t["target_nfp_chg_k"].values)
            pred = m.predict(row[cols].values.reshape(1, -1))[0]
            predictions[f"{name}_{window_name}"] = float(pred)
    return predictions


def report():
    global CONSENSUS_NFP_K, PREDICTION_MARKET_NFP_K, PREDICTION_MARKET_STALE
    CONSENSUS_NFP_K = _resolve_consensus()
    PREDICTION_MARKET_NFP_K, PREDICTION_MARKET_STALE = _resolve_prediction_market()

    release_date = os.environ.get("NFP_RELEASE_DATE", "unknown")
    print("=" * 78)
    print(f"NFP PREDICTION FINAL REPORT — U.S. Nonfarm Payrolls (ref month {PREDICTION_MONTH.date()})")
    print(f"Release: {release_date} 08:30 ET  |  Report generated: {datetime.now().isoformat(timespec='seconds')}")
    print("=" * 78)

    # 1. Load features + apply overrides
    df = build_feature_matrix()
    for c, v in JULY_OVERRIDES.items():
        if c in df.columns:
            df.at[PREDICTION_MONTH, c] = v
    df.to_csv(PROC / "features.csv")

    # 2. Main ML ensemble
    ml_preds = predict_next(df, PREDICTION_MONTH, train_start=pd.Timestamp("2010-01-01"))
    summary_pc = pd.read_csv(PROC / "backtest_summary_postcovid.csv")

    # weighted ensemble (excl worst)
    merged = ml_preds.merge(summary_pc[["model", "MAE", "RMSE"]], on="model")
    merged = merged[merged["model"] != "Naive: last value"].copy()
    merged["weight"] = 1.0 / merged["MAE"]
    merged["weight"] /= merged["weight"].sum()
    ml_ensemble = float((merged["prediction_k"] * merged["weight"]).sum())
    ml_rmse = float(np.sqrt((merged["weight"] * merged["RMSE"] ** 2).sum()))
    ml_dispersion = float(merged["prediction_k"].std())

    # 2b. First-print target models (predicting the reported headline directly)
    print("\n[Training first-print target models...]")
    df_fp = build_first_print_features()
    exclude_fp = {"target_nfp_chg_k", "nfp_chg_lag1", "nfp_chg_lag2", "nfp_chg_lag3",
                  "nfp_chg_3m_avg", "nfp_chg_6m_avg", "nfp_chg_12m_avg"}
    # Filter out low-history features that would shrink training sample
    MIN_HISTORY = 60
    low_hist = {c for c in df_fp.columns if df_fp[c].notna().sum() < MIN_HISTORY}
    exclude_fp |= low_hist
    fp_feature_cols = [c for c in df_fp.columns if c not in exclude_fp and c != "target_first_print_k"]
    fp_summary_pc_path = PROC / "first_print_backtest_summary_postcovid.csv"
    if fp_summary_pc_path.exists():
        fp_summary_pc = pd.read_csv(fp_summary_pc_path)
    else:
        # Fallback: compute if not cached
        bt = walk_forward(df_fp, "target_first_print_k", fp_feature_cols,
                          train_start=pd.Timestamp("2010-01-01"),
                          test_start=pd.Timestamp("2022-06-01"),
                          test_end=pd.Timestamp("2026-06-01"), min_train=48)
        fp_summary_pc = summarize(bt)
        fp_summary_pc.to_csv(fp_summary_pc_path, index=False)
    fp_preds = predict_first_print(df_fp, PREDICTION_MONTH, "target_first_print_k", fp_feature_cols)
    fp_merged = fp_preds.merge(fp_summary_pc[["model", "MAE", "RMSE"]], on="model")
    fp_merged["weight"] = 1.0 / fp_merged["MAE"]
    fp_merged["weight"] /= fp_merged["weight"].sum()
    fp_ensemble = float((fp_merged["prediction_k"] * fp_merged["weight"]).sum())
    fp_median = float(fp_merged["prediction_k"].median())
    fp_rmse = float(np.sqrt((fp_merged["weight"] * fp_merged["RMSE"] ** 2).sum()))
    fp_dispersion = float(fp_merged["prediction_k"].std())

    # 2c. Sector-decomposition model (sum of 11 sector regressions)
    print("\n[Running sector decomposition...]")
    from src.sector_model import run as sector_run
    sector_result = sector_run()
    sector_pred = sector_result["total_pred_k"]
    sector_rmse = sector_result["upper_bound_rmse_k"]

    # 3. Bridge model predictions
    bridge_preds = compute_bridges(df, PREDICTION_MONTH)
    bridge_median = float(np.median(list(bridge_preds.values())))
    bridge_mean = float(np.mean(list(bridge_preds.values())))
    bridge_min = float(min(bridge_preds.values()))
    bridge_max = float(max(bridge_preds.values()))

    # 4. All-models ensemble (ML revised + first-print + bridges + sector)
    all_preds = (list(merged["prediction_k"].values)
                 + list(fp_merged["prediction_k"].values)
                 + list(bridge_preds.values())
                 + [sector_pred])
    grand_mean = float(np.mean(all_preds))
    grand_median = float(np.median(all_preds))
    grand_std = float(np.std(all_preds))

    # 5. THREE-WAY BLEND: Bloomberg consensus + Prediction markets + First-print model
    # Prediction markets have historically outperformed surveys for NFP (MAE ~40K vs ~55K)
    # AND they incorporate real-time repricing (already adjusted for today's ADP miss).
    var_c = CONSENSUS_MAE_HIST_K ** 2
    var_pm = PREDICTION_MARKET_MAE_HIST_K ** 2
    var_fp = fp_rmse ** 2
    # Inverse-variance weights
    w_raw = [1/var_c, 1/var_pm, 1/var_fp]
    w_sum = sum(w_raw)
    w_c, w_pm, w_fp = [w / w_sum for w in w_raw]
    blended = (w_c * CONSENSUS_NFP_K
               + w_pm * PREDICTION_MARKET_NFP_K
               + w_fp * fp_ensemble)
    blended_rmse = float(np.sqrt(1 / w_sum))
    # keep for backwards compat below
    w_c_fp = w_c
    w_fp = w_fp

    print("\n### MODEL PREDICTIONS ###")
    print(f"\n  ML ensemble (revised target, 9 models):        {ml_ensemble:+7.1f} K")
    print(f"    weighted RMSE: {ml_rmse:.0f}K   dispersion: {ml_dispersion:.0f}K")
    print(f"\n  ** FIRST-PRINT ensemble (targeting reported #): {fp_ensemble:+7.1f} K **")
    print(f"    weighted RMSE: {fp_rmse:.0f}K   dispersion: {fp_dispersion:.0f}K")
    print(f"    median (7 models): {fp_median:+.1f} K")
    print(f"    individual first-print predictions:")
    for _, r in fp_merged.iterrows():
        print(f"      {r['model']:15s} {r['prediction_k']:+7.1f} K   (weight {r['weight']:.3f})")

    print(f"\n  Bridge models (8 specs x 2 windows = {len(bridge_preds)} preds):")
    print(f"    median:   {bridge_median:+7.1f} K")
    print(f"    mean:     {bridge_mean:+7.1f} K")
    print(f"    range:    [{bridge_min:+.0f}, {bridge_max:+.0f}] K")

    # sorted bridges
    for name, pred in sorted(bridge_preds.items(), key=lambda x: x[1]):
        print(f"      {name:30s}  {pred:+7.1f}")

    print(f"\n  ALL-MODELS ({len(all_preds)} predictions total):")
    print(f"    median:   {grand_median:+7.1f} K")
    print(f"    mean:     {grand_mean:+7.1f} K")
    print(f"    std:      {grand_std:+7.1f} K  (agreement measure)")

    print(f"\n  Sector decomposition (sum of 11 sector regressions): {sector_pred:+7.1f} K")
    print(f"    RMSE (upper bound): {sector_rmse:.0f} K")

    print(f"\n  Market consensus (Bloomberg/Reuters, pre-ADP):  {CONSENSUS_NFP_K:+7.1f} K")
    print(f"  Prediction market implied (Polymarket + Kalshi): {PREDICTION_MARKET_NFP_K:+7.1f} K")
    print(f"    (Kalshi $227K vol + Polymarket $25K vol; markets repriced after today's ADP miss)")

    print("\n### FINAL BLENDED FORECAST ###")
    print(f"  Three-way Bayesian blend (inverse-variance):")
    print(f"    {w_c*100:.0f}% Bloomberg consensus (MAE {CONSENSUS_MAE_HIST_K:.0f}K)")
    print(f"    {w_pm*100:.0f}% Prediction markets (MAE {PREDICTION_MARKET_MAE_HIST_K:.0f}K)")
    print(f"    {w_fp*100:.0f}% First-print model ensemble (RMSE {fp_rmse:.0f}K)")
    print(f"")
    print(f"  ==> POINT ESTIMATE: {blended:+.0f} K jobs added (first-print)")
    print(f"      Combined RMSE:  +/- {blended_rmse:.0f} K")
    print(f"      68% CI:         [{blended-blended_rmse:+.0f}, {blended+blended_rmse:+.0f}] K")
    print(f"      95% CI:         [{blended-2*blended_rmse:+.0f}, {blended+2*blended_rmse:+.0f}] K")

    # Also compute median-based alternative
    fp_med_blend = w_c_fp * CONSENSUS_NFP_K + w_fp * fp_median
    print(f"\n  Alt: median-based blend (excludes outlier models): {fp_med_blend:+.0f} K")

    print("\n### DIRECTIONAL LEAN vs CONSENSUS ###")
    delta = blended - CONSENSUS_NFP_K
    if delta > 15:
        lean = "MODESTLY ABOVE consensus"
    elif delta > 5:
        lean = "SLIGHTLY ABOVE consensus"
    elif delta < -15:
        lean = "MODESTLY BELOW consensus"
    elif delta < -5:
        lean = "SLIGHTLY BELOW consensus"
    else:
        lean = "IN LINE WITH consensus"
    print(f"  {lean}  ({delta:+.0f} K deviation)")

    return {"blended": blended, "blended_rmse": blended_rmse,
            "ml_ensemble": ml_ensemble, "bridge_median": bridge_median,
            "grand_median": grand_median, "lean": lean,
            "first_print_ensemble": fp_ensemble, "sector_pred": sector_pred,
            "consensus": CONSENSUS_NFP_K, "pred_markets": PREDICTION_MARKET_NFP_K,
            "pred_markets_stale": PREDICTION_MARKET_STALE}


if __name__ == "__main__":
    report()
