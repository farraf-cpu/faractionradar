# Richmond Fed Manufacturing Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Richmond Fed Manufacturing Composite Index (monthly, ~4th Tuesday, 10:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-richmond.yml`

## What v1-simple-blend does

Consensus + naive anchor. FRED trend deferred to v1.1 pending series-ID verification.

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~5 |
| Last-known anchor | live from calendar-worker `?read` (previous field) | ~7 |

Value format: signed `+8.5` / `-3.2` (0 = neutral).

## Positioning

Fifth and final regional Fed survey each month — completes the 5-Fed
composite proxy for ISM Mfg (Empire + Philly + Dallas + KC + Richmond).
5th district covers Mid-Atlantic: VA, MD, NC, SC, WV.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 27th event covered.
