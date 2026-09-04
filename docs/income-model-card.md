# Personal Income Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Personal Income m/m (monthly, ~last business day, 08:30 ET, BEA)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-income.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:20 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.15 |
| FRED PI 3-mo m/m trend | mean of last 3 m/m %-changes of nominal Personal Income | ~0.20 |

Value format: `+0.3%` m/m.

## Positioning

Nominal Personal Income (wages + salaries + transfers + rents + interest
+ dividends). Released same day/time as PCE Price Index and Personal
Spending — the BEA income + outlays trio. The income-vs-spending gap is
the household savings pulse the Fed watches for consumption sustainability.

## Change log

- **v1-simple-blend** — first ship. Completes BEA income + outlays trio.
