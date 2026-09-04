# BOC Overnight Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** BOC Overnight Rate (~8x/year, ~14:45 UTC Wednesdays)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-boc.yml`

## What v2-outcome-distribution does

Same architecture as FOMC/ECB/BOE/BOJ/RBA v2: point estimate + 25bp
outcome distribution. BOC has been steadily normalizing since 2024;
moves are typically 25bp increments.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Overnight Rate anchor | FRED `IRSTCI01CAM156N` (OECD Immediate <24h CA) | ~0.15 |

## Method notes

- **IRSTCI01CAM156N tracks BOC overnight rate within ~5-10bp**,
  monthly updates. FRED `INTDSRCAM193N` (CA Discount Rate)
  discontinued since 2013 — Rule 27 (universal Discount-Rate-Dead).
- **8 meetings/year**: ~every 6 weeks on Wednesdays. All 2026-2027
  meeting dates hardcoded in worker.
- **Monetary Policy Report**: released 4x/year at rate decisions
  (Jan/Apr/Jul/Oct). Additional signal beyond rate itself.

## What v2 does NOT do (yet)

- **No BAX (3-month bankers' acceptance) futures curve** — direct
  market-implied rate path would replace or augment anchor.
- **No MPR sentiment index.**
- **Empirical variance calibration** blocked on resolutions.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 6 CAD
  expansion opens.
