# Consumer Credit Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Consumer Credit m/m Change (monthly, ~5-8th, 15:00 ET, Fed G.19)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-credit.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:05 UTC daily.

| Sub-model | Source | Historical MAE ($B) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~$5.0B |
| FRED TOTALSL 3-mo mean m/m change | total consumer credit outstanding | ~$8.0B |

Value format: `+$12.5B` (signed $B m/m change).

## Positioning

Federal Reserve G.19 report. Combined revolving (credit cards) +
non-revolving (auto + student loans) consumer credit outstanding.
Volatile series — student-loan reclassifications and auto-loan seasonal
shifts can flip signs month-to-month. Revolving-credit sub-index
(Phase 2) is the cleaner consumer-confidence signal.

## Change log

- **v1-simple-blend** — first ship.
