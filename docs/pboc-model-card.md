# PBOC 1Y LPR Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** PBOC 1-Year Loan Prime Rate (monthly, ~20th at 09:15 CST / 01:15 UTC)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-pboc.yml`

## What v2-outcome-distribution does

Same architecture as other v2 rate predictors: point estimate + 25bp
outcome distribution.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current PBOC Discount Rate | FRED `INTDSRCNM193N` | ~0.30 |

## Method notes

- **Anchor caveat:** FRED `INTDSRCNM193N` (PBOC Discount Rate) is the
  best live-ish CN anchor available. Unlike UK/JP/AU/CA (where
  INTDSR* is dead — Rule 27), CN keeps this series updated, though
  with a ~15-month reporting lag. Typically tracks LPR within ~20bp
  but may lag genuine policy shifts.
- **SHIBOR fallback:** `IR3TIB01CNM156N` (3-mo SHIBOR) is fresher
  (1-2 month lag) but sits ~160bp below LPR — unusable as a scale
  anchor. Dropped.
- **Outcome distribution caveat:** because INTDSRCNM193N lags,
  outcome distribution may false-positive "hike" when the anchor
  hasn't caught up to actual policy. Users should weight consensus
  higher when interpreting.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 10 CNY
  expansion opens.
