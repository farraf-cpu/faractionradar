# UK CPI prediction - target 2026-09-17 (T-13)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T17:03:44.096729+00:00

## Final pick

**+3.7%** y/y UK CPI

- Regime: above-target inflation
- 68% CI: [+3.47%, +3.87%]
- 95% CI: [+3.27%, +4.07%]
- Lean vs consensus: no consensus
- Sub-models used: trend

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

- **v1-simple-blend (2026-09-04)** - first ship.
