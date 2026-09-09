# Core Retail Sales prediction — target 2026-09-16 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-09T10:37:27.524965+00:00

## Final pick

**+0.7%** m/m Core Retail Sales (ex food + energy)

- Regime: strong consumer spending
- 68% CI: [+0.55%, +0.85%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.40%, +1.00%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.08pp |
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

- **v1-simple-blend (2026-09-09)** — first ship.
