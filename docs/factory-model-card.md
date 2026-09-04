# Factory Orders Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Factory Orders m/m (monthly, ~first week of month, 10:00 ET, Census M3 Survey full report)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-factory.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:40 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.3 |
| FRED AMTMNO 3-mo mean m/m | manufacturers' total new orders | ~0.5 |

Value format: `+0.5%` m/m.

## Positioning

Full M3 Survey report from Census — adds nondurable orders + revised
durables + inventories on top of the advance Durable Goods print already
released ~5-7 business days earlier. Aircraft-order cycles make the
headline volatile; ex-transportation is the cleaner signal (Phase 2
sub-model).

## Change log

- **v1-simple-blend** — first ship.
