# BCB Policy Rate prediction - target 2026-09-16 (T-4)

**Model version:** `v2.1-wide-buckets`
**Published:** 2026-09-12T18:40:57.499881+00:00

## Final pick

**21.00%** BCB Policy Rate

- 68% CI: [20.70%, 21.30%] · sigma source: prior (inverse-MAE)
- 95% CI: [20.40%, 21.60%]
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
| anchor | 21.00% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
INTDSRBRM193N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 15 (BRL expansion) rate-decision predictor. BCB meets
~~12x/year (monthly Copom meeting). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-12)** - first ship. Phase 15 BRL expansion opens.
