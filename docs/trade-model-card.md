# Trade Balance Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Trade Balance (monthly, ~1st week, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-trade.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED BOPGSTB 3-month trend.
Cron 15:10 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE ($ B) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~3 |
| FRED BOPGSTB 3-month trend | mean of last 3 Trade Balance readings (goods + services, converted M→B) | ~4 |

## Value format

Signed dollar billions with $ prefix. `-$78.5B` (typical deficit) or
`+$5.0B` (rare surplus). Regime: narrower deficit (≥-$60B) / typical
(-$60 to -$80B) / wide (-$80 to -$100B) / extreme (<-$100B).

## Why this feeds GDP

Net exports = Exports − Imports is a direct GDP component. A wider trade
deficit subtracts from GDP nowcasts. Any Phase 2 GDPNow-style work on
`predict-gdp.yml` will consume this predictor's output as an input.

## Phase 2 targets

- **Advance Goods Trade Balance** — separate slug `trade-adv-<date>` for
  the goods-only preliminary release (~1 week before Combined). Leads
  Combined directionally
- **Petroleum trade balance carve-out** — oil-price swings distort headline
- **DXY cross-check** — 3-month DXY change correlates ~-0.4 with headline
  (stronger dollar → wider deficit)

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 16th event covered.
