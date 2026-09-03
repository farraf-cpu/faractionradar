# Building Permits Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Building Permits (monthly, ~16-19th, 08:30 ET, Census Bureau)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-permits.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:10 UTC daily.

| Sub-model | Source | Historical MAE (K annualized) |
|-----------|--------|-------------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~40 |
| FRED PERMIT 3-mo trend | mean of last 3 Building Permits values (SA) | ~60 |

Value format: `1.42M` annualized.

## Positioning

Forward-looking housing indicator — builders pull permits 1-2 months
before breaking ground. Cleaner rate-sensitivity read than Housing
Starts (which is confounded by weather + crew availability). Released
same day/time as Housing Starts, so the Permits/Starts spread is a
tradeable read: Permits > Starts ratio rising = builder confidence
returning ahead of realized construction.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 28th event covered.
