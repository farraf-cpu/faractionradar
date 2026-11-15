# NB Policy Rate prediction - target 2026-09-17 (T-12)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T23:20:38.686647+00:00

## Final pick

**1.72%** NB Policy Rate

- 68% CI: [1.57%, 1.87%]
- 95% CI: [1.42%, 2.02%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
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
