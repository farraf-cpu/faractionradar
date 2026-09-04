# Swiss CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** Swiss CPI y/y (monthly, ~1 week after reference month, 07:30 UTC winter / 08:30 CET, BFS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-chcpi.yml`

## What v1-simple-blend does

Consensus-only. FRED's `CPALTT01CHM659N` exists but is stale
(last obs 2025-04) — usable as a slow-moving fallback but not
tight enough for a real 3-mo mean anchor.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" CHF | ~0.15 |

## Positioning

Second Phase 8 CHF predictor. Swiss inflation is characteristically
low (typically 0-1% y/y); SNB targets 0-2% (price stability, not a
point target).

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 8 CHF expansion.
  Consensus-only pending BFS Statistical Portal API integration.
