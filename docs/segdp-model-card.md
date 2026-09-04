# SE GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** SE GDP q/q (~9 weeks after quarter end, 07:30 UTC / 09:30 CEST, SCB)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-segdp.yml`

## What v1-simple-blend does

Inverse-MAE blend of 2 sub-models. Quarterly cadence.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "GDP q/q" SEK | ~0.15 |
| FRED CLVMNACSCAB1GQSE 4-qtr trend | mean of last 4 published q/q %-changes (OECD chained real GDP SE) | ~0.30 |

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 9 SEK expansion.
