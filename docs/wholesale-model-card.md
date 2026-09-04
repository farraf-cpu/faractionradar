# Wholesale Inventories Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Wholesale Inventories m/m (monthly, ~day 8-10, 10:00 ET, Census Monthly Wholesale Trade)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-wholesale.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:00 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.15 |
| FRED WHLSLRIMSA 3-mo mean m/m | merchant wholesalers inventories | ~0.25 |

Value format: `+0.2%` m/m.

## Positioning

Merchant wholesalers inventories — the leading sector in the
inventory-cycle chain. Full report ~day 9 (~1 week before Business
Inventories). Wholesalers absorb demand shocks first before feeding
back into mfg orders. Wholesale-to-sales ratio (Phase 2) is the
sharper signal for demand-vs-stock imbalance.

## Change log

- **v1-simple-blend** — first ship.
