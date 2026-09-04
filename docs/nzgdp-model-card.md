# NZ GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** NZ GDP q/q (~11 weeks after quarter end, 21:45 UTC prior day / 10:45 NZDT, StatsNZ)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-nzgdp.yml`

## What v1-simple-blend does

Consensus-only point estimate — FRED `NGDPRSAXDCNZQ` doesn't exist;
`CPALTT01NZQ659N` also dead.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "GDP q/q" NZD | ~0.15 |

Soft-skips when consensus missing.

## Positioning

Third Phase 7 NZD predictor. Quarterly cadence — 4 fires/year.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 7 NZD expansion.
  Consensus-only pending StatsNZ Infoshare API integration.
