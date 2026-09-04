# Norges Bank Policy Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** Norges Bank Policy Rate (~8x/year, 09:00 UTC / 10:00 CET)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-norges.yml`

## What v2-outcome-distribution does

Same architecture as other v2 rate predictors: point estimate + 25bp
outcome distribution.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Policy Rate | FRED `IRSTCI01NOM156N` (OECD Immediate <24h NO) | ~0.15 |

## Method notes

- **NO has BETTER FRED coverage than SE/NZ.** `IRSTCI01NOM156N`
  (OECD Immediate Rates <24h) is LIVE and current (2026-06), unlike
  SE where the same series is 6 years stale. This means normal
  MAE 0.15pp (not inflated).
- Norges Bank meets 8x/year with detailed Monetary Policy Reports
  4x. Rate policy has been steady in the mid-4% range since 2024.

## What v2 does NOT do (yet)

- No NIBOR/FRA curve integration
- Empirical variance calibration blocked on resolutions

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 11 NOK
  expansion opens. Nordic pair complete (SE + NO).
