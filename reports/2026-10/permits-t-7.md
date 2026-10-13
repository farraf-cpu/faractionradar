# Building Permits prediction — target 2026-10-20 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-13T21:14:52.633544+00:00

## Final pick

**1.40M** annualized permits

- Regime: typical forward pipeline
- 68% CI: [1.34M, 1.46M] · sigma source: prior (inverse-MAE)
- 95% CI: [1.28M, 1.52M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 40K |
| trend | 1.40M | 60K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
PERMIT 3-month trend. Same publication window as Housing Starts.

## Positioning

Forward-looking housing indicator — builders pull permits 1-2 months
before breaking ground. Cleaner rate-sensitivity read than Starts
(which is confounded by weather / construction crew availability).

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 28th event covered.
