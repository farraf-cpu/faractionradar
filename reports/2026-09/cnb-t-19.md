# CNB Policy Rate prediction - target 2026-09-24 (T-19)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:58:37.148685+00:00

## Final pick

**3.52%** CNB Policy Rate

- 68% CI: [3.47%, 3.57%]
- 95% CI: [3.41%, 3.63%]
- Lean vs anchor: -6bp cut vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 3.50% | 0.05pp |
| anchor | 3.58% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01CZM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 19 (CZK expansion) rate-decision predictor. CNB meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 19 CZK expansion opens.
