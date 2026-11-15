# RBA Cash Rate prediction - target 2026-09-30 (T-26)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T17:54:27.736208+00:00

## Final pick

**4.35%** RBA Cash Rate

- 68% CI: [4.20%, 4.50%]
- 95% CI: [4.05%, 4.65%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 4.35% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01AUM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 5 (AUD expansion) rate-decision predictor. RBA MPC meets
~11x/year (2024 reform reduced from monthly except January). 25bp
buckets match FOMC/ECB/BOE/BOJ for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 5 AUD expansion opens.
