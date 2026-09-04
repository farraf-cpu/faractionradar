# Core PCE prediction — target 2026-09-22 (T-18)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-04T10:24:34.459928+00:00

## Final pick

**+0.2%** m/m Core PCE (ex food + energy)

- Regime: on-target core inflation
- 68% CI: [+0.13%, +0.21%]
- 95% CI: [+0.09%, +0.25%]
- Lean vs consensus: no consensus
- Sub-models used: cleveland_fed, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.05pp |
| cleveland_fed | +0.13% | 0.04pp |
| trend | +0.28% | 0.10pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of FF consensus +
Cleveland Fed daily nowcast (when CPI cycle active) + FRED PCEPILFE
6-month m/m trend.

## Positioning

Core PCE (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core PCE strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-09-04)** — first ship.
