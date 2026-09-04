# CBI Policy Rate prediction - target 2026-10-07 (T-32)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T23:12:52.333495+00:00

## Final pick

**7.72%** CBI Policy Rate

- 68% CI: [7.67%, 7.78%]
- 95% CI: [7.62%, 7.83%]
- Lean vs anchor: +8bp move vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 7.75% | 0.05pp |
| anchor | 7.64% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01ISM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 24 (ISK expansion) rate-decision predictor. CBI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 24 ISK expansion opens.
