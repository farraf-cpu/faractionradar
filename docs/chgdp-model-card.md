# Swiss GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** Swiss GDP q/q (~9 weeks after quarter end, 08:00 UTC winter / 09:00 CET, SECO)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-chgdp.yml`

## What v1-simple-blend does

Inverse-MAE blend of 2 sub-models. Quarterly cadence — 4 fires/year.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "GDP q/q" CHF | ~0.15 |
| FRED CLVMNACSCAB1GQCH 4-qtr trend | mean of last 4 published q/q %-changes (OECD chained real GDP CH) | ~0.30 |

## Positioning

Third Phase 8 CHF predictor. SECO publishes Swiss quarterly GDP ~9
weeks after quarter end.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 8 CHF expansion.
