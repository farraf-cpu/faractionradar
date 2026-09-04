# Import Prices prediction — target 2026-09-16 (T-12)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T08:07:51.708680+00:00

## Final pick

**+0.3%** m/m Import Price Index

- Regime: modest import inflation
- 68% CI: [-0.06%, +0.74%]
- 95% CI: [-0.46%, +1.14%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.20pp |
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

- **v1-simple-blend (2026-09-04)** — first ship.
