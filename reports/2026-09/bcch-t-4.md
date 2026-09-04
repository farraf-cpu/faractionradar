# BCCH Policy Rate prediction - target 2026-09-09 (T-4)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T22:39:30.993540+00:00

## Final pick

**4.50%** BCCH Policy Rate

- 68% CI: [4.35%, 4.65%]
- 95% CI: [4.20%, 4.80%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 4.50% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01CLM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 22 (CLP expansion) rate-decision predictor. BCCH meets
~8x/year (monthly). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 22 CLP expansion opens.
