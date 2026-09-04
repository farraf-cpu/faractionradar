# NB Policy Rate prediction - target 2026-09-17 (T-12)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T23:12:01.577716+00:00

## Final pick

**1.74%** NB Policy Rate

- 68% CI: [1.69%, 1.80%]
- 95% CI: [1.64%, 1.85%]
- Lean vs anchor: +2bp move vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 1.75% | 0.05pp |
| anchor | 1.72% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01DKM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 23 (DKK expansion) rate-decision predictor. NB meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 23 DKK expansion opens.
