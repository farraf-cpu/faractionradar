# Core PPI prediction — target 2026-09-10 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-10T10:42:31.756243+00:00

## Final pick

**+0.3%** m/m Core PPI (ex food + energy)

- Regime: elevated core wholesale inflation
- 68% CI: [+0.23%, +0.38%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.16%, +0.45%]
- Lean vs consensus: in line with consensus
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
| consensus | +0.30% | 0.08pp |
| trend | +0.31% | 0.15pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
PPIFES 6-month m/m trend.

## Positioning

Core PPI (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core PPI strips
those to show underlying inflation trend. Sticky-Fed indicator —
prints >0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

## Change log

- **v1-simple-blend (2026-09-10)** — first ship.
