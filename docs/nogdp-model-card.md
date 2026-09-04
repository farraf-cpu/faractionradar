# NO GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** NO GDP q/q (~9 weeks after quarter end, 07:00 UTC / 09:00 CET, SSB)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-nogdp.yml`

## What v1-simple-blend does

Inverse-MAE blend. Quarterly cadence.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "GDP q/q" NOK | ~0.15 |
| FRED CLVMNACSCAB1GQNO 4-qtr trend | mean of last 4 published q/q %-changes (OECD chained real GDP NO) | ~0.30 |

## Positioning

Third Phase 11 NOK predictor. Note: NO Mainland GDP (excluding oil
& gas + shipping) is typically the trader focus; this predictor
targets headline GDP.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 11 NOK expansion.
