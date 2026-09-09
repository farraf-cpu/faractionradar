# Export Prices prediction — target 2026-09-16 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-09T17:41:35.902357+00:00

## Final pick

**+1.1%** m/m Export Prices (ex food + energy)

- Regime: strong export price gains
- 68% CI: [+0.91%, +1.21%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.76%, +1.36%]
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
| trend | +1.06% | 0.15pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
IQ 6-month m/m trend.

## Positioning

Export Prices (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Export Prices strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-09-09)** — first ship.
