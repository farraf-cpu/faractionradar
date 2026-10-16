# MNB Policy Rate prediction - target 2026-10-20 (T-4)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-10-16T21:32:39.521722+00:00

## Final pick

**5.71%** MNB Policy Rate

- 68% CI: [5.56%, 5.86%] · sigma source: prior (inverse-MAE)
- 95% CI: [5.41%, 6.01%]
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
| anchor | 5.71% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01HUM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 20 (HUF expansion) rate-decision predictor. MNB meets
~12x/year (monthly). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-10-16)** - first ship. Phase 20 HUF expansion opens.
