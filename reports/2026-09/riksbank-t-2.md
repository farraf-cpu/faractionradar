# RIKSBANK Policy Rate prediction - target 2026-09-24 (T-2)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-22T18:39:24.787795+00:00

## Final pick

**1.97%** RIKSBANK Policy Rate

- 68% CI: [1.67%, 2.27%] · sigma source: prior (inverse-MAE)
- 95% CI: [1.37%, 2.57%]
- Lean vs anchor: hold expected
- Sub-models used: anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 10.6% |
| +25bp hike | 23.3% |
| hold | 32.3% **(modal)** |
| -25bp cut | 23.3% |
| -50bp cut | 8.7% |
| -75bp or deeper | 1.9% |



## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.30 pp |
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
| anchor | 1.97% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IR3TIB01SEM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 9 (SEK expansion) rate-decision predictor. RIKSBANK meets
~~6x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-22)** - first ship. Phase 9 SEK expansion opens.
