# UK CPI prediction - target 2026-09-17 (T-13)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T16:49:33.920245+00:00

## Final pick

**+3.0%** y/y UK CPI

- Regime: above-target inflation
- 68% CI: [+2.93%, +3.12%]
- 95% CI: [+2.83%, +3.21%]
- Lean vs consensus: above consensus by 0.32pp
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.70% | 0.10pp |
| trend | +3.67% | 0.20pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CPALTT01GBM659N 3-mo mean y/y trend.

## Positioning

First Phase 3 (GBP expansion) inflation predictor. UK CPI released
by ONS ~mid-month for previous month. BoE target is 2.0% CPI y/y.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship.
