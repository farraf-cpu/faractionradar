# Advance Goods Trade Balance Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Advance Goods Trade Balance (monthly, ~last week of month, 08:30 ET, BEA)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-adtrade.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:50 UTC daily.

| Sub-model | Source | Historical MAE ($B) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~$3.0B |
| FRED BOPGTB 3-mo mean anchor | Goods Trade Balance, BOP basis | ~$5.0B |

Value format: `-$118.8B` (signed $B; deficits negative).

## Positioning

Goods-only trade balance released ~10 days ahead of the full Trade
Balance report. Advance report → market-moving import/export mix
signal for GDP nowcasts; the goods-services split lands with the full
report. Leading indicator on Q/Q GDP net-exports contribution.

Distinct from the `trade` predictor which covers the full BEA
International Trade (goods + services) release ~day 6 of month.

## Change log

- **v1-simple-blend** — first ship.
