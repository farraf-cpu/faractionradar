# CN GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** CN GDP y/y (quarterly, ~16 days after quarter end, 02:00 UTC / 10:00 CST, NBS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-cngdp.yml`

## What v1-simple-blend does

Consensus-only. Both `CLVMNACSCAB1GQCN` and `CHNGDPNQDSMEI` are
missing/dead on FRED.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "GDP y/y" CNY | ~0.15 |

## Positioning

Third Phase 10 CNY predictor. Notably early release (~16 days after
quarter end) compared to Western economies. Trader event around
5% government target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 10 CNY expansion.
