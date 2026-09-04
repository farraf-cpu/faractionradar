# NO CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** NO CPI y/y (monthly, ~10th of following month, 06:00 UTC / 08:00 CET, SSB)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-nocpi.yml`

## What v1-simple-blend does

Consensus-only. FRED `CPALTT01NOM659N` stale since 2025-04.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" NOK | ~0.15 |

## Positioning

Second Phase 11 NOK predictor. Norges Bank targets 2% CPI y/y. NO
CPI includes both headline and core (CPI-ATE) measures; this
predictor targets headline.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 11 NOK expansion.
