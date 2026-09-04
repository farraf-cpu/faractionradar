# Core CPI prediction — target 2026-09-11 (T-7)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-04T10:01:45.306929+00:00

## Final pick

**+0.2%** m/m Core CPI (ex food + energy)

- Regime: on-target core inflation
- 68% CI: [+0.05%, +0.35%]
- 95% CI: [-0.10%, +0.50%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.08pp |
| cleveland_fed | — | 0.06pp |
| trend | +0.20% | 0.15pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of FF consensus +
Cleveland Fed daily nowcast (when CPI cycle active) + FRED CPILFESL
6-month m/m trend.

## Positioning

Core CPI (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core CPI strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-09-04)** — first ship.
