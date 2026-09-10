# BOE Bank Rate prediction - target 2026-09-17 (T-7)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-10T09:07:38.726601+00:00

## Final pick

**3.73%** BoE Bank Rate

- 68% CI: [3.48%, 3.98%] · sigma source: prior (inverse-MAE)
- 95% CI: [3.23%, 4.23%]
- Lean vs anchor: hold expected
- Sub-models used: anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 6.7% |
| +25bp hike | 24.2% |
| hold | 38.3% **(modal)** |
| -25bp cut | 24.2% |
| -50bp cut | 6.1% |
| -75bp or deeper | 0.6% |



## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.25 pp |
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
| anchor | 3.73% | 0.25pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IUDSOIA (SONIA) current-rate anchor. Point + sigma discretized over 25bp
buckets via normal CDF integration for outcome probabilities.

## Positioning

First Phase 3 (GBP expansion) rate-decision predictor. BoE MPC meets
~8x/year. Bank Rate is the primary policy instrument. Distribution
covers standard hike50/hike25/hold/cut25/cut50/cut75+ outcomes.

## Change log

- **v2-outcome-distribution (2026-09-10)** - first ship. Phase 3 GBP expansion opens.
