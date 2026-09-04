# CN CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** CN CPI y/y (monthly, ~9-15th of following month, 09:30 CST, NBS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-cncpi.yml`

## What v1-simple-blend does

Consensus-only. FRED `CPALTT01CNM659N` stale since 2025-04.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" CNY | ~0.15 |

## Positioning

Second Phase 10 CNY predictor. CN inflation has been running near
deflation (0% or slightly negative) since mid-2024; PBOC watching
closely but does not have explicit CPI target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 10 CNY expansion.
  Consensus-only pending NBS national data API integration.
