# RBI Policy Rate prediction - target 2026-10-01 (T-26)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:14:09.281327+00:00

## Final pick

**5.50%** RBI Policy Rate

- 68% CI: [5.43%, 5.57%]
- 95% CI: [5.37%, 5.63%]
- Lean vs anchor: hold expected
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 5.50% | 0.05pp |
| anchor | 5.50% | 1.00pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01INM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 14 (INR expansion) rate-decision predictor. RBI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 14 INR expansion opens.
