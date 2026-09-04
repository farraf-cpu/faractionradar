# BI Policy Rate prediction - target 2026-09-17 (T-12)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T23:13:55.602113+00:00

## Final pick

**5.78%** BI Policy Rate

- 68% CI: [5.73%, 5.84%]
- 95% CI: [5.68%, 5.89%]
- Lean vs anchor: -10bp cut vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 5.75% | 0.05pp |
| anchor | 5.88% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01IDM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 25 (IDR expansion) rate-decision predictor. BI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 25 IDR expansion opens.
