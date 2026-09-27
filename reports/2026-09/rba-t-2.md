# RBA Cash Rate prediction - target 2026-09-29 (T-2)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-27T18:42:46.758882+00:00

## Final pick

**4.54%** RBA Cash Rate

- 68% CI: [4.48%, 4.59%] · sigma source: prior (inverse-MAE)
- 95% CI: [4.43%, 4.64%]
- Lean vs anchor: +19bp move vs current rate
- Sub-models used: consensus, anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 0.0% |
| +25bp hike | 88.1% **(modal)** |
| hold | 11.9% |
| -25bp cut | 0.0% |
| -50bp cut | 0.0% |
| -75bp or deeper | 0.0% |



## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.05 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 4.60% | 0.05pp |
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

- **v2-outcome-distribution (2026-09-27)** - first ship. Phase 5 AUD expansion opens.
