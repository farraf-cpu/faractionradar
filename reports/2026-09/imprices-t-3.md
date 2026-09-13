# Import Prices prediction — target 2026-09-16 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-13T17:23:34.538897+00:00

## Final pick

**+0.1%** m/m Import Price Index

- Regime: flat import prices
- 68% CI: [-0.07%, +0.30%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.26%, +0.49%]
- Lean vs consensus: above consensus by 0.11pp
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.20 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.00% | 0.20pp |
| trend | +0.34% | 0.40pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
IR 3-month m/m trend.

## Positioning

Early inflation input — tariff shocks, oil prices, and currency moves
flow through import prices before CPI. Fed watches for pass-through
timing on import-heavy consumer categories. Ex-petroleum sub-index
(Phase 2) isolates the core-goods component.

## Change log

- **v1-simple-blend (2026-09-13)** — first ship.
