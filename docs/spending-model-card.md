# Personal Spending Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Personal Spending m/m (monthly, ~last business day, 08:30 ET, BEA)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-spending.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:15 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.15 |
| FRED PCE 3-mo m/m trend | mean of last 3 m/m %-changes of nominal PCE | ~0.20 |

Value format: `+0.4%` m/m.

## Positioning

Personal Consumption Expenditures (nominal). ~70% of US GDP is consumer
spending — this is the core consumer-demand pulse the Fed watches.
Released same day/time as PCE Price Index; spending-vs-prices split is
the real-vs-nominal consumer read.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 29th event covered.
