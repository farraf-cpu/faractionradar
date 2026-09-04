# CA CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** CA CPI y/y (monthly, ~3 weeks after reference month, 13:30 UTC, StatCan)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-cacpi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to 2 sub-models. Monthly
cadence.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" CAD | ~0.15 |
| FRED CPALTT01CAM659N 3-mo trend | mean of last 3 published y/y %-changes (OECD CA CPI) | ~0.30 |

## Positioning

Second Phase 6 CAD predictor. StatCan publishes CPI y/y monthly ~3
weeks after reference month. BOC target 2% CPI y/y (1-3% band).

## What v1 does NOT do (yet)

- **No CPI-trim / CPI-median / CPI-common** — BOC's preferred core
  measures (three variants). Would give a more direct BOC-relevant
  underlying signal. Phase 6.1.
- **No StatCan API integration** for real-time index level tracking.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 6 CAD expansion.
