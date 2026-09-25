# RBA Cash Rate prediction - target 2026-09-29 (T-4)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-25T18:42:16.571945+00:00

## Final pick

**4.35%** RBA Cash Rate

- 68% CI: [4.20%, 4.50%] · sigma source: prior (inverse-MAE)
- 95% CI: [4.05%, 4.65%]
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



## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


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

- **v2-outcome-distribution (2026-09-25)** - first ship. Phase 5 AUD expansion opens.
