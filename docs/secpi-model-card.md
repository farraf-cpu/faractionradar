# SE CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** SE CPI y/y (monthly, ~2 weeks after reference month, 07:00 UTC / 08:00 CET, SCB)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-secpi.yml`

## What v1-simple-blend does

Consensus-only. FRED `CPALTT01SEM659N` stale since 2025-03.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" SEK | ~0.15 |

## Positioning

Second Phase 9 SEK predictor. Riksbank targets 2% CPI y/y with
tolerance band; SE inflation has been running below target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 9 SEK expansion.
  Consensus-only pending SCB Statistical Portal API integration.
