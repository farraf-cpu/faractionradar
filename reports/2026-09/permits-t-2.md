# Building Permits prediction — target 2026-09-17 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-15T16:23:25.129499+00:00

## Final pick

**1.40M** annualized permits

- Regime: typical forward pipeline
- 68% CI: [1.37M, 1.44M] · sigma source: prior (inverse-MAE)
- 95% CI: [1.33M, 1.47M]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 40.00 K |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 1.40M | 40K |
| trend | 1.41M | 60K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
PERMIT 3-month trend. Same publication window as Housing Starts.

## Positioning

Forward-looking housing indicator — builders pull permits 1-2 months
before breaking ground. Cleaner rate-sensitivity read than Starts
(which is confounded by weather / construction crew availability).

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 28th event covered.
