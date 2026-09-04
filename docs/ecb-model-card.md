# ECB Rate Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** ECB Main Refinancing Rate (~8x/year, Governing Council meetings, 13:15 CET, ECB)
**Status:** Live (Phase 2, EUR expansion) - cadence T-7/4/3/2/1 via `predict-ecb.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:45 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.05 |
| FRED ECBDFR current-rate anchor | ECB Deposit Facility Rate | ~0.25 |

Value format: `2.25%` (rate level, 2 decimals).

## Positioning

First Phase 2 predictor. ECB Governing Council meets ~8x/year to set
the Deposit Facility Rate (primary policy rate since 2022). Historical
consensus MAE is very tight because analysts triangulate from ECB
speaker comments + market pricing. Anchor is no-change baseline.

Phase 2 target: outcome distribution + eurodollar futures implied rate
(similar to FOMC v2 planning).

## Change log

- **v1-simple-blend** - first ship. Phase 2 EUR expansion opens.
