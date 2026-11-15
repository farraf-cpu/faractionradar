# Import Prices prediction — target 2026-10-16 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-09T21:41:00.111234+00:00

## Final pick

**+0.0%** m/m Import Price Index

- Regime: flat import prices
- 68% CI: [-0.38%, +0.42%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.78%, +0.82%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.20pp |
| trend | +0.02% | 0.40pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
IR 3-month m/m trend.

## Positioning

Early inflation input — tariff shocks, oil prices, and currency moves
flow through import prices before CPI. Fed watches for pass-through
timing on import-heavy consumer categories. Ex-petroleum sub-index
(Phase 2) isolates the core-goods component.

## Change log

- **v1-simple-blend (2026-10-09)** — first ship.
