# S&P/Case-Shiller HPI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US S&P/Case-Shiller 20-City Composite HPI y/y (monthly, last Tuesday, 09:00 ET, S&P Cotality)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-caseshiller.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:30 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.15 |
| FRED SPCS20RSA 3-mo mean y/y | 12-mo % change, SA | ~0.25 |

Value format: `+2.1%` y/y.

## Positioning

Reports 2-month-lag data (September release covers July). Trend is smooth,
so the FRED-anchor sub-model is competitive with consensus. Home-price
appreciation is the wealth-effect input for consumption forecasts and a
lagging read on shelter-inflation direction the Fed watches.

## Change log

- **v1-simple-blend** — first ship.
