# Export Prices prediction — target 2026-11-17 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-15T22:00:12.114903+00:00

## Final pick

**+1.0%** m/m Export Prices (ex food + energy)

- Regime: strong export price gains
- 68% CI: [+0.84%, +1.14%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.69%, +1.29%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.08pp |
| trend | +0.99% | 0.15pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
IQ 6-month m/m trend.

## Positioning

Export Prices (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Export Prices strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-11-15)** — first ship.
