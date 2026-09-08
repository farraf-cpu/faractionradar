# ECB Rate prediction - target 2026-09-10 (T-2)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-08T11:27:59.563790+00:00

## Final pick

**2.58%** ECB Deposit Facility Rate

- 68% CI: [2.52%, 2.64%] · sigma source: prior (inverse-MAE)
- 95% CI: [2.47%, 2.70%]
- Lean vs anchor: +33bp move vs current rate
- Sub-models used: consensus, anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 24.0% |
| +25bp hike | 76.0% **(modal)** |
| hold | 0.0% |
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
| consensus | 2.65% | 0.05pp |
| anchor | 2.25% | 0.25pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
ECBDFR current-rate anchor. Consensus MAE tight on rate-decision days
because analysts converge on likely move; anchor is no-change baseline.

## Positioning

First Phase 2 (EUR expansion) predictor. ECB Governing Council meets
~8x/year. Deposit Facility Rate is the primary ECB policy rate since
2022. Phase 2 target adds outcome distribution + eurodollar futures
implied rate similar to FOMC v2.

## Change log

- **v1-simple-blend (2026-09-08)** - first ship. Phase 2 EUR expansion opens.
