# Philly Fed Manufacturing Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Philly Fed Manufacturing Index (monthly, ~3rd Thursday, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-philly.yml`

## What v1-simple-blend does

Consensus + naive anchor. FRED trend deferred to v1.1 pending series-ID verification.

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~4 |
| Last-known anchor | live from calendar-worker `?read` (previous field) | ~6 |

Value format: signed `+8.5` / `-3.2` (0 = neutral).

## Positioning

Second regional Fed survey each month (after Empire on ~15th). Empire +
Philly composite is early bird for ISM Manufacturing signal.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 24th event covered.
