# Core Retail Sales prediction — target 2026-09-16 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-14T17:40:47.728112+00:00

## Final pick

**+0.6%** m/m Core Retail Sales (ex food + energy)

- Regime: strong consumer spending
- 68% CI: [+0.49%, +0.64%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.42%, +0.72%]
- Lean vs consensus: above consensus by 0.07pp
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.08 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.50% | 0.08pp |
| trend | +0.70% | 0.15pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
RSFSXMV 6-month m/m trend.

## Positioning

Core Retail Sales (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core Retail Sales strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-09-14)** — first ship.
