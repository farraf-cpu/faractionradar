# Building Permits prediction — target 2026-11-19 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-18T22:56:46.282586+00:00

## Final pick

**1.37M** annualized permits

- Regime: typical forward pipeline
- 68% CI: [1.31M, 1.43M] · sigma source: prior (inverse-MAE)
- 95% CI: [1.25M, 1.49M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 40K |
| trend | 1.37M | 60K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
PERMIT 3-month trend. Same publication window as Housing Starts.

## Positioning

Forward-looking housing indicator — builders pull permits 1-2 months
before breaking ground. Cleaner rate-sensitivity read than Starts
(which is confounded by weather / construction crew availability).

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 28th event covered.
