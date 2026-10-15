# Core Retail Sales prediction — target 2026-10-16 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-15T15:10:25.697192+00:00

## Final pick

**+0.6%** m/m Core Retail Sales (ex food + energy)

- Regime: strong consumer spending
- 68% CI: [+0.49%, +0.79%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.34%, +0.94%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.08pp |
| trend | +0.64% | 0.15pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
RSFSXMV 6-month m/m trend.

## Positioning

Core Retail Sales (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core Retail Sales strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-10-15)** — first ship.
