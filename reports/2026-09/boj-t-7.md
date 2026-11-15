# BOJ Policy Rate prediction - target 2026-09-19 (T-7)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-12T18:24:25.482735+00:00

## Final pick

**0.84%** BOJ Policy Rate

- 68% CI: [0.69%, 0.99%] · sigma source: prior (inverse-MAE)
- 95% CI: [0.54%, 1.14%]
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
| anchor | 0.84% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01JPM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF integration for outcome probabilities.

## Positioning

First Phase 4 (JPY expansion) rate-decision predictor. BOJ MPC meets
~8x/year. Post-2024 exit from NIRP, BOJ moves in 15-25bp steps.
25bp buckets match FOMC/ECB/BOE for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-12)** - first ship. Phase 4 JPY expansion opens.
