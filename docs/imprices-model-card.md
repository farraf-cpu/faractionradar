# Import Prices Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Import Prices m/m (monthly, ~day 15-17, 08:30 ET, BLS)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-imprices.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:10 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.2 |
| FRED IR 3-mo mean m/m | Import Price Index | ~0.4 |

Value format: `+0.3%` m/m.

## Positioning

Early inflation input — tariff shocks, oil prices, and currency moves
flow through import prices before CPI. Fed watches for pass-through
timing on import-heavy consumer categories. Ex-petroleum sub-index
(Phase 2) isolates the core-goods component.

## Change log

- **v1-simple-blend** — first ship.
