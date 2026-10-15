# BOK Policy Rate prediction - target 2026-10-22 (T-7)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-10-15T06:03:25.218121+00:00

## Final pick

**2.81%** BOK Policy Rate

- 68% CI: [2.66%, 2.96%] · sigma source: prior (inverse-MAE)
- 95% CI: [2.51%, 3.11%]
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
| anchor | 2.81% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01KRM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 12 (KRW expansion) rate-decision predictor. BOK meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-10-15)** - first ship. Phase 12 KRW expansion opens.
