# UK CPI prediction - target 2026-10-15 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-14T09:38:42.474418+00:00

## Final pick

**+3.7%** y/y UK CPI

- Regime: above-target inflation
- 68% CI: [+3.47%, +3.87%] · sigma source: prior (inverse-MAE)
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

- **v1-simple-blend (2026-10-14)** - first ship.
