# Capacity Utilization Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Capacity Utilization Rate (monthly, ~mid-month, 09:15 ET, Federal Reserve G.17)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-caputil.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:25 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.2 |
| FRED TCU 3-mo mean anchor | last 3 months of Cap Util level | ~0.4 |

Value format: `76.3%` (level percentage, one decimal, %-suffixed).

## Positioning

Federal Reserve G.17 release, published simultaneously with Industrial
Production (same day, same time). Cap Util measures the ratio of actual
output to sustainable maximum output across manufacturing + mining +
utilities.

Regime bands:
- ≥80% — tight capacity (inflationary pressure)
- 75-80% — healthy utilization
- 70-75% — slack capacity
- <70% — deep slack

Fed watches it as a capacity-side inflation input alongside labor slack.

## Change log

- **v1-simple-blend** — first ship. Pairs with IndPro (same-day release).
