# Core Retail Sales prediction — target 2026-11-17 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-15T21:59:02.218063+00:00

## Final pick

**+0.5%** m/m Core Retail Sales (ex food + energy)

- Regime: strong consumer spending
- 68% CI: [+0.41%, +0.56%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.34%, +0.63%]
- Lean vs consensus: above consensus by 0.08pp
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.40% | 0.08pp |
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

- **v1-simple-blend (2026-11-15)** — first ship.
