# CBRT Policy Rate prediction - target 2026-10-22 (T-4)

**Model version:** `v2.1-wide-buckets`
**Published:** 2026-10-18T20:56:36.419540+00:00

## Final pick

**38.75%** CBRT Policy Rate

- 68% CI: [38.45%, 39.05%] · sigma source: prior (inverse-MAE)
- 95% CI: [38.15%, 39.35%]
- Lean vs anchor: hold expected
- Sub-models used: anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 0.0% |
| +25bp hike | 4.8% |
| hold | 90.4% **(modal)** |
| -25bp cut | 4.8% |
| -50bp cut | 0.0% |
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
| anchor | 38.75% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
INTDSRTRM193N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 17 (TRY expansion) rate-decision predictor. CBRT meets
~~12x/year (monthly CBRT meeting). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-10-18)** - first ship. Phase 17 TRY expansion opens.
