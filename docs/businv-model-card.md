# Business Inventories Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Business Inventories m/m (monthly, ~mid-month, 10:00 ET, Census Manufacturing & Trade Inventories & Sales)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-businv.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:55 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.15 |
| FRED BUSINV 3-mo mean m/m | total business inventories, nominal | ~0.25 |

Value format: `+0.2%` m/m.

## Positioning

Combines manufacturers + wholesalers + retailers inventory levels.
Watched by GDP nowcasters — inventory-change is a direct component of
GDP. Sustained buildup (>0.5% m/m) signals slowing sales absorption
and often precedes production slowdowns. Inventory-to-sales ratio
(Phase 2 sub-model) sharpens the demand-vs-stock signal.

## Change log

- **v1-simple-blend** — first ship.
