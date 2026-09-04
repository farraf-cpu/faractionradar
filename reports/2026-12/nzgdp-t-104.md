# NZ GDP prediction - target 2026-12-17 (T-104)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:06:06.818988+00:00

## Final pick

**+0.4%** q/q NZ GDP

- Regime: modest growth
- 68% CI: [+0.25%, +0.55%]
- 95% CI: [+0.10%, +0.70%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.40% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (StatsNZ monthly GDP is not on FRED
cleanly; StatsNZ API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 7 (NZD expansion) predictor. NZ GDP released by
StatsNZ ~11 weeks after quarter end at 10:45 NZDT (21:45 UTC prior day). Sits alongside
BoE Bank Rate + CA CPI in Phase 7 NZD trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 7.1 target: integrate StatsNZ
`stats.govt.nz` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 7 NZD predictor. Consensus-only pending StatsNZ API integration.
