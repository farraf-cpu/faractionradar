# SNB Policy Rate prediction - target 2026-09-25 (T-21)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T20:21:45.566454+00:00

## Final pick

**-0.04%** SNB Policy Rate

- 68% CI: [-0.34%, 0.26%]
- 95% CI: [-0.65%, 0.55%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | -0.04% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IR3TIB01CHM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 8 (CHF expansion) rate-decision predictor. SNB meets
~4x/year (quarterly). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 8 CHF expansion opens.
