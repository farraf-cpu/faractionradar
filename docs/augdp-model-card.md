# AU GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** AU GDP q/q (quarterly, ~9 weeks after quarter end, 00:30 UTC / 11:30 AEDT, ABS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-augdp.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to 2 sub-models. Quarterly
cadence — 4 fires/year.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` → matched FF `forecast` for "GDP q/q" AUD | ~0.15 |
| FRED NGDPRSAXDCAUQ 4-qtr trend | mean of last 4 published q/q %-changes (real GDP AU) | ~0.30 |

## Positioning

Third Phase 5 AUD predictor. AU quarterly GDP released ~9 weeks after
quarter end by ABS. Big trader event on AUD given RBA's growth
sensitivity.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 5 AUD expansion.
