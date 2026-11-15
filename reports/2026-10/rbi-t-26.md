# RBI Policy Rate prediction - target 2026-10-01 (T-26)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:19:25.625588+00:00

## Final pick

**5.50%** RBI Policy Rate

- 68% CI: [4.50%, 6.50%]
- 95% CI: [3.50%, 7.50%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
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
