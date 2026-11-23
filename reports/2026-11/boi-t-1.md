# BOI Policy Rate prediction - target 2026-11-24 (T-1)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-11-23T09:34:06.771388+00:00

## Final pick

**3.25%** BOI Policy Rate

- 68% CI: [3.10%, 3.40%] · sigma source: prior (inverse-MAE)
- 95% CI: [2.95%, 3.55%]
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
| anchor | 3.25% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01ILM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 18 (ILS expansion) rate-decision predictor. BOI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-11-23)** - first ship. Phase 18 ILS expansion opens.
