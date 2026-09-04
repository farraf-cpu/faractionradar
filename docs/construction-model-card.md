# Construction Spending Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Construction Spending m/m (monthly, 1st business day, 10:00 ET, Census)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-construction.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:45 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.3 |
| FRED TTLCONS 3-mo mean m/m | total construction spending, nominal | ~0.4 |

Value format: `+0.5%` m/m.

## Positioning

Nominal outlays across residential + nonresidential + public
construction. 2-month data lag makes the FRED-anchor sub-model
competitive with consensus. Residential-vs-nonresidential split
(Phase 2) is where the leading signal lives — housing pipeline vs
manufacturing/infra pipeline diverge under different macro regimes.

## Change log

- **v1-simple-blend** — first ship.
