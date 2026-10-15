# Core PPI prediction — target 2026-10-15 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-15T20:26:10.565403+00:00

## Final pick

**+0.3%** m/m Core PPI (ex food + energy)

- Regime: elevated core wholesale inflation
- 68% CI: [+0.26%, +0.41%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.19%, +0.48%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.30% | 0.08pp |
| trend | +0.40% | 0.15pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
PPIFES 6-month m/m trend.

## Positioning

Core PPI (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core PPI strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-10-15)** — first ship.
