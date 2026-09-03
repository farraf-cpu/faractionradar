# KC Fed Manufacturing Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US KC Fed Manufacturing Composite Index (monthly, ~4th Thursday, 11:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-kcfed.yml`

## What v1-simple-blend does

Consensus + naive anchor. FRED trend deferred to v1.1 pending series-ID verification.

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~4 |
| Last-known anchor | live from calendar-worker `?read` (previous field) | ~6 |

Value format: signed `+8.5` / `-3.2` (0 = neutral).

## Positioning

Fourth regional Fed survey each month (after Empire, Philly, Dallas).
KC's 10th district covers Plains states — agriculture + energy exposure.
Feeds the 5-Fed composite proxy for ISM Mfg.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 26th event covered.
