# Eurozone CPI prediction - target 2026-09-17 (T-13)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T10:53:52.568141+00:00

## Final pick

**+2.9%** y/y Eurozone HICP

- Regime: above-target inflation
- 68% CI: [+2.74%, +3.14%]
- 95% CI: [+2.54%, +3.34%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.10pp |
| trend | +2.94% | 0.20pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CP0000EZ19M086NEST 3-mo mean y/y trend.

## Positioning

Second Phase 2 predictor. Eurozone Flash Estimate released ~1st
business day of following month; final print follows ~2 weeks later.
ECB's inflation target is 2.0% HICP y/y. Above-target since post-COVID.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship.
