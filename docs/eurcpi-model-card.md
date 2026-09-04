# Eurozone CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** Eurozone CPI Flash Estimate y/y (monthly, ~1st business day of following month, 11:00 CET, Eurostat)
**Status:** Live (Phase 2, EUR expansion) - cadence T-7/4/3/2/1 via `predict-eurcpi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:50 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.10 |
| FRED CP0000EZ19M086NEST 3-mo mean y/y | HICP Total Euro Area 19 | ~0.20 |

Value format: `+2.9%` y/y.

## Positioning

Second Phase 2 predictor. Eurozone Flash Estimate released ~1st business
day of following month; final print follows ~2 weeks later. ECB's
inflation target is 2.0% HICP y/y. Above-target since post-COVID.

## Change log

- **v1-simple-blend** - first ship. Second Phase 2 EUR predictor.
