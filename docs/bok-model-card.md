# BOK Base Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** Bank of Korea Base Rate (~8x/year, 01:00 UTC / 10:00 KST)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-bok.yml`

## What v2-outcome-distribution does

Same architecture as other v2 rate predictors.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Base Rate | FRED `IRSTCI01KRM156N` (OECD Immediate <24h KR, LIVE) | ~0.15 |

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 12 KRW
  expansion opens.
