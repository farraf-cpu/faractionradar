# UK CPI prediction - target 2026-09-17 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-13T04:36:28.199508+00:00

## Final pick

**+3.7%** y/y UK CPI

- Regime: above-target inflation
- 68% CI: [+3.47%, +3.87%] · sigma source: prior (inverse-MAE)
- 95% CI: [+3.27%, +4.07%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.20 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.10pp |
| trend | +3.67% | 0.20pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CPALTT01GBM659N 3-mo mean y/y trend.

## Positioning

First Phase 3 (GBP expansion) inflation predictor. UK CPI released
by ONS ~mid-month for previous month. BoE target is 2.0% CPI y/y.

## Change log

- **v1-simple-blend (2026-09-13)** - first ship.
