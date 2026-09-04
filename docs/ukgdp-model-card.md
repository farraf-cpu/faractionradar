# UK Monthly GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** UK Monthly GDP m/m (~40 day lag, 07:00 UK time, ONS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-ukgdp.yml`

## What v1-simple-blend does

Consensus-only point estimate. Cron 18:10 UTC daily + 04:00 UTC on
release day.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` for "GDP m/m" GBP | ~0.15 |

Soft-skips (no prediction shipped) when FF consensus missing.

## Why consensus-only

UK Monthly GDP is published by ONS but not carried on FRED cleanly.
Alternatives require ONS `api.ons.gov.uk` timeseries integration
(deferred to v1.1). This mirrors the German IFO pattern where
proprietary source blocks a FRED-anchor sub-model.

## Positioning

Third Phase 3 GBP predictor. UK Monthly GDP is the reliable trader
event vs quarterly GDP — released monthly with ~40 day lag.

## What v1 does NOT do (yet)

- **No trend anchor** — ONS API integration would give a real 3-mo mean.
- **No Index of Services sub-model** — services are ~80% of UK GDP;
  a dedicated services-only anchor could reduce sigma.
- **No Industrial Production sub-model** — smaller share but volatile
  contributor.

## Phase 3.1+ target

- Integrate ONS `api.ons.gov.uk` timeseries (`IHYQ` monthly GDP;
  `ELBH` services m/m; `K222` industrial production m/m).

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 3 GBP expansion.
  Consensus-only pending ONS API integration.
