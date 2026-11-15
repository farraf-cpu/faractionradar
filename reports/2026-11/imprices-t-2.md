# Import Prices prediction — target 2026-11-17 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-15T21:47:01.373786+00:00

## Final pick

**+0.6%** m/m Import Price Index

- Regime: modest import inflation
- 68% CI: [+0.42%, +0.80%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.23%, +0.98%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.70% | 0.20pp |
| trend | +0.42% | 0.40pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
IR 3-month m/m trend.

## Positioning

Early inflation input — tariff shocks, oil prices, and currency moves
flow through import prices before CPI. Fed watches for pass-through
timing on import-heavy consumer categories. Ex-petroleum sub-index
(Phase 2) isolates the core-goods component.

## Change log

- **v1-simple-blend (2026-11-15)** — first ship.
