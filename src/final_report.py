"""Final synthesis: combine ML ensemble + bridge models + consensus + signal balance
into a comprehensive prediction report."""
from __future__ import annotations

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

CONSENSUS_NFP_K = 85.0   # REVISED post-ADP (was +120K pre-release, now +80-88K range)
CONSENSUS_MAE_HIST_K = 55.0

# Prediction market data (from Polymarket + Kalshi screenshots 2026-08-05 late afternoon)
# Polymarket "How many jobs added in July?" ($25K vol): modal 50-100K at 40%,
#   weighted midpoint EV ~85K
# Kalshi "Jobs numbers in July 2026?" ($227K vol, higher liquidity, better signal):
#   Above 60K 64%, Above 70K 58%, Above 80K 41% => implied central estimate ~80K
# Averaging both markets (Kalshi weighted higher due to volume): ~82K
PREDICTION_MARKET_NFP_K = 82.0
PREDICTION_MARKET_MAE_HIST_K = 40.0  # prediction markets historically ~40K MAE for NFP


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
    print("=" * 78)
    print(f"NFP PREDICTION FINAL REPORT — U.S. Nonfarm Payrolls (July 2026 ref)")
    print(f"Release: Fri Aug 7 2026 08:30 ET  |  Report generated: {datetime.now().isoformat(timespec='seconds')}")
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

    # 6. Print report
    print("\n### KNOWN INPUTS FOR JULY 2026 ###")
    print(f"  ADP Nonfarm Private (Jul):    +68K  (vs 98K consensus — MISS -30K)")
    print(f"  Jobless Claims 4wk avg:      ~203K  (LOW — labor market not deteriorating)")
    print(f"  ISM Mfg Employment (Jul):    52.8  (up +3.1, expansion first time in 33mo)")
    print(f"  Empire State employment:     11.4  (positive)")
    print(f"  Philly Fed employment:       10.0  (positive)")
    print(f"  UMich Consumer Sentiment:    55.2  (5-month high, +11.5% MoM)")
    print(f"  Challenger Job Cuts:      62,075   (+29% MoM, +140% YoY — BEARISH)")
    print(f"  Prior month NFP (Jun):       +57K  (weak print)")

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

    print("\n### SIGNAL BALANCE ###")
    print("  BULLISH signals:")
    print("    + ISM Mfg Employment breakout (+3.1, first expansion in 33mo)")
    print("    + Jobless claims LOW (~203K 4wk avg)")
    print("    + UMich sentiment 5-month high (55.2)")
    print("    + Empire/Philly Fed employment positive")
    print("  BEARISH signals:")
    print("    - ADP MISS (+68K vs 98K consensus, -30K)")
    print("    - Challenger job cuts SURGE (+140% YoY)")
    print("    - Prior NFP (Jun) was WEAK (+57K)")
    print("    - Trend deceleration (12mo avg only +42K)")

    # Save markdown report
    md_path = REPORTS / f"final_forecast_{PREDICTION_MONTH.strftime('%Y_%m')}.md"
    with open(md_path, "w") as f:
        f.write(f"# NFP Forecast — July 2026 (release Fri Aug 7 2026)\n\n")
        f.write(f"Generated: {datetime.now().isoformat(timespec='seconds')}\n\n")
        f.write(f"## Final blended forecast\n\n")
        f.write(f"**{blended:+.0f}K jobs**  (68% CI [{blended-blended_rmse:+.0f}, {blended+blended_rmse:+.0f}])\n\n")
        f.write(f"Directional lean: **{lean}** ({delta:+.0f}K deviation)\n\n")
        f.write(f"## Components\n\n")
        f.write(f"| Component | Point | RMSE |\n|---|---|---|\n")
        f.write(f"| ML ensemble (9 models) | {ml_ensemble:+.0f}K | {ml_rmse:.0f}K |\n")
        f.write(f"| Bridge models (median of {len(bridge_preds)}) | {bridge_median:+.0f}K | ~110K |\n")
        f.write(f"| All-models grand median | {grand_median:+.0f}K | dispersion {grand_std:.0f}K |\n")
        f.write(f"| Consensus (Bloomberg pre-ADP) | {CONSENSUS_NFP_K:+.0f}K | {CONSENSUS_MAE_HIST_K:.0f}K |\n")
        f.write(f"| **Blended (Bayesian)** | **{blended:+.0f}K** | **{blended_rmse:.0f}K** |\n\n")
        f.write(f"## Known inputs used\n\n")
        f.write(f"- ADP Jul: +68K (miss -30K)\n")
        f.write(f"- Jobless claims 4wk: ~203K (low)\n")
        f.write(f"- ISM Mfg Employment: 52.8 (+3.1 breakout)\n")
        f.write(f"- Empire/Philly Fed employment: positive\n")
        f.write(f"- UMich Sentiment: 55.2 (5mo high)\n")
        f.write(f"- Challenger cuts: 62,075 (+140% YoY)\n\n")
        f.write(f"## All model predictions\n\n")
        f.write(f"```\n{merged[['model','prediction_k','MAE']].to_string(index=False)}\n```\n\n")
        f.write(f"### Bridge models\n\n```\n")
        for name, pred in sorted(bridge_preds.items(), key=lambda x: x[1]):
            f.write(f"{name:30s}  {pred:+7.1f}K\n")
        f.write(f"```\n")
    print(f"\nReport saved: {md_path}")

    return {"blended": blended, "blended_rmse": blended_rmse,
            "ml_ensemble": ml_ensemble, "bridge_median": bridge_median,
            "grand_median": grand_median, "lean": lean,
            "first_print_ensemble": fp_ensemble, "sector_pred": sector_pred,
            "consensus": CONSENSUS_NFP_K, "pred_markets": PREDICTION_MARKET_NFP_K}


if __name__ == "__main__":
    report()
