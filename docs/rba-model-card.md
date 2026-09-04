# RBA Cash Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** RBA Cash Rate (MPC decision, ~11x/year post-2024, 03:30 UTC / 14:30 AEDT)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-rba.yml`

## What v2-outcome-distribution does

Same architecture as FOMC/ECB/BOE/BOJ v2: point estimate + probability
distribution over standard 25bp buckets. RBA moves are always 25bp
increments (no negative rate regime).

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Cash Rate anchor | FRED `IRSTCI01AUM156N` (OECD Immediate Rates <24h AU) | ~0.15 |

## Method notes

- **IRSTCI01AUM156N tracks RBA Cash Rate within ~5-10bp**, updates
  monthly. FRED `INTDSRAUM193N` (AU Discount Rate) is discontinued
  since 2013 — Rule 23 (universal Discount-Rate-Dead pattern).
- **Post-2024 RBA reform:** meets 8x/year → 11x/year (one meeting
  per month except January). All schedule dates for 2026-2027 are
  hardcoded in the worker.

## What v2 does NOT do (yet)

- **No ASX 30-day interbank cash rate futures** — direct market-implied
  path would be an obvious v2.1 upgrade.
- **No RBA minutes / speech hawkishness index.**
- **Empirical variance calibration** blocked on resolutions.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 5 AUD
  expansion opens.
