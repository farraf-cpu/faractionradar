# CBI Policy Rate prediction - target 2026-10-07 (T-4)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-10-03T21:42:13.398191+00:00

## Final pick

**7.89%** CBI Policy Rate

- 68% CI: [7.74%, 8.04%] · sigma source: prior (inverse-MAE)
- 95% CI: [7.59%, 8.19%]
- Lean vs anchor: hold expected
- Sub-models used: anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 0.6% |
| +25bp hike | 19.6% |
| hold | 59.5% **(modal)** |
| -25bp cut | 19.6% |
| -50bp cut | 0.6% |
| -75bp or deeper | 0.0% |


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 7.89% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01ISM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 24 (ISK expansion) rate-decision predictor. CBI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-10-03)** - first ship. Phase 24 ISK expansion opens.
