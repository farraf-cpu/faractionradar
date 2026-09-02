"""One-shot orchestrator — called by the launcher.

Steps:
  1. Refresh FRED data (fast, ~30 sec)
  2. Rebuild features + apply manual overrides
  3. Run all model layers + generate final report
  4. Print prominent forecast panel
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

RELEASE_DATE = os.environ.get("NFP_RELEASE_DATE", "unknown")

BANNER = f"""
================================================================================
                    U.S. NONFARM PAYROLLS PREDICTOR
                    Target release: {RELEASE_DATE} 08:30 ET
================================================================================
"""


def step(title: str):
    print(f"\n>>> {title}")


def main(refresh_data: bool = True):
    t0 = time.time()
    print(BANNER)

    if refresh_data:
        step("1/4 Refreshing FRED data (34 series)...")
        try:
            from src.fred_fetch import fetch_all
            fetch_all()
        except Exception as e:
            print(f"[warn] FRED refresh failed ({e}) — using cached CSVs")

    step("2/4 Building feature matrix...")
    from src.build_features import build_feature_matrix, PREDICTION_MONTH
    df = build_feature_matrix()
    print(f"  Feature matrix: {df.shape}, target date: {PREDICTION_MONTH.date()}")

    step("3/4 Running full model stack (this takes ~1 min)...")
    from src.final_report import report
    result = report()

    step("4/4 DONE")
    elapsed = time.time() - t0

    # ------------- prominent forecast panel -------------
    b = result["blended"]
    r = result["blended_rmse"]

    # HUGE final-pick banner FIRST — impossible to miss
    print()
    print("#" * 80)
    print("#" + " " * 78 + "#")
    print("#" + f"           >>>  MY FINAL PICK:  {b:+.0f} K  jobs  <<<".ljust(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" + f"           Release: {RELEASE_DATE} 08:30 ET".ljust(78) + "#")
    print("#" + f"           Confidence: 68% chance the print lands in [{b-r:+.0f}, {b+r:+.0f}] K".ljust(78) + "#")
    print("#" + " " * 78 + "#")
    print("#" * 80)

    # Then the detailed component breakdown
    print()
    print("+" + "=" * 78 + "+")
    print(f"|  DETAIL: how the final pick was computed".ljust(79) + "|")
    print("+" + "-" * 78 + "+")
    print(f"|                                                                              |")
    print(f"|      POINT ESTIMATE:  {b:+8.0f} K jobs                                           |")
    print(f"|      68% CI:          [{b-r:+.0f}, {b+r:+.0f}] K                                             |")
    print(f"|      95% CI:          [{b-2*r:+.0f}, {b+2*r:+.0f}] K                                             |")
    print(f"|      Lean vs cons:    {result['lean']:<40s}         |")
    print(f"|                                                                              |")
    print("+" + "-" * 78 + "+")
    print(f"|  Ingredients (each feeds into the final pick above):                         |")
    print(f"|    Bloomberg consensus:          {result['consensus']:+7.0f} K   (weight: high - 55K historical MAE)|")
    print(f"|    Prediction markets (avg):     {result['pred_markets']:+7.0f} K   (weight: high - 40K historical MAE)|")
    print(f"|    ML ensemble (revised):        {result['ml_ensemble']:+7.0f} K                                   |")
    print(f"|    First-print ensemble:         {result['first_print_ensemble']:+7.0f} K                                   |")
    print(f"|    Bridge models median:         {result['bridge_median']:+7.0f} K                                   |")
    print(f"|    Sector decomposition (11):    {result['sector_pred']:+7.0f} K                                   |")
    print(f"|    Grand median (all models):    {result['grand_median']:+7.0f} K                                   |")
    print(f"|    -----                                                                     |")
    print(f"|    Blended (Bayesian FINAL):     {b:+7.0f} K   <-- THIS IS THE ANSWER          |")
    print("+" + "=" * 78 + "+")
    print()
    print(f"Runtime: {elapsed:.1f} seconds")
    return result


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--no-refresh", action="store_true", help="skip FRED data refresh")
    args = p.parse_args()
    main(refresh_data=not args.no_refresh)
