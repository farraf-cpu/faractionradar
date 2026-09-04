# Monthly Treasury Budget Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Federal Budget Balance (monthly, ~day 8-13, 14:00 ET, Treasury Bureau of the Fiscal Service)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-budget.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:15 UTC daily.

| Sub-model | Source | Historical MAE ($B) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~$15B |
| FRED MTSDS133FMS same-month-last-year anchor | prior year same month | ~$40B |

Year-ago is preferred over 3-mo mean anchor because of strong
quarterly tax-payment seasonality.

Value format: `-$432.3B` (typical deficit) or `+$215.0B` (April surplus,
rare tax-season).

## Positioning

Federal fiscal balance. Market watches for Treasury supply guidance and
Fed liquidity effects. Wide deficits (< -$200B) pressure Treasury
issuance; surprising surpluses (tax-season only) reduce near-term
supply. Debt-ceiling episodes make this print market-moving.

## Change log

- **v1-simple-blend** — first ship.
