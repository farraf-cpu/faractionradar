# NZ CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** NZ CPI y/y (quarterly, ~1 month after quarter end, 21:45 UTC prior day / 10:45 NZDT, StatsNZ)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-nzcpi.yml`

## What v1-simple-blend does

Consensus-only point estimate — FRED's `CPALTT01NZQ659N` is
discontinued (last obs 2023).

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" NZD | ~0.15 |

Soft-skips when consensus missing.

## Positioning

Second Phase 7 NZD predictor. Quarterly cadence — 4 fires/year.
RBNZ targets 2% CPI y/y (1-3% band).

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 7 NZD expansion.
  Consensus-only pending StatsNZ Infoshare API integration.
