# Dallas Fed Manufacturing Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Dallas Fed Manufacturing Index (monthly, ~last Monday, 10:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-dallas.yml`

## What v1-simple-blend does

Consensus + naive anchor. FRED trend deferred to v1.1 pending series-ID verification.

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~5 |
| Last-known anchor | live from calendar-worker `?read` (previous field) | ~7 |

Value format: signed `+8.5` / `-3.2` (0 = neutral).

## Positioning

Third regional Fed survey each month (after Empire ~15th, Philly ~3rd
Thursday). Texas leans oil-heavy — Dallas is the highest-beta regional
Fed to WTI crude swings. Feeds the 5-Fed composite proxy for ISM Mfg.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 25th event covered.
