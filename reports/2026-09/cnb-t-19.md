# CNB Policy Rate prediction - target 2026-09-24 (T-19)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T22:04:13.060170+00:00

## Final pick

**3.58%** CNB Policy Rate

- 68% CI: [3.43%, 3.73%]
- 95% CI: [3.28%, 3.88%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
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
