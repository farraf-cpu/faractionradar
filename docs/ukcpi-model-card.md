# UK CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** UK CPI y/y (monthly, ~mid-month, 07:00 UK time, ONS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-ukcpi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to 2 sub-models. Cron
18:05 UTC daily + 04:30 UTC on release day.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` for "CPI y/y" GBP | ~0.10 |
| FRED CPALTT01GBM659N 3-mo trend | mean of last 3 published y/y %-changes of UK CPI | ~0.20 |

Weights are `1 / MAE`. Consensus dominates when present.

## Positioning

Second Phase 3 GBP predictor (after BOE Bank Rate). BoE's inflation
target is 2.0% CPI y/y. UK CPI print releases ~15-17th of month
covering previous month's data.

## What v1 does NOT do (yet)

- **Not a core-CPI model.** Headline y/y only. Core UK CPI is Phase 3.1.
- **No services CPI carve-out.** Services CPI is BoE's preferred
  underlying-inflation signal. Would tighten posterior.
- **Not a true Bayesian model** — inverse-MAE priors from benchmark,
  not empirical variance.

## Phase 3.1+ target

- Core UK CPI split (headline vs core headline)
- Services CPI sub-model (BoE's preferred underlying signal)
- ONS release-day timing model (some prints land within seconds; others
  drift by ~30s of processing lag on their site)

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 3 GBP expansion.
