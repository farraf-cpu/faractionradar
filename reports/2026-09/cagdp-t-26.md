# CA Monthly GDP prediction - target 2026-09-30 (T-26)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T18:04:45.916585+00:00

## Final pick

**+0.3%** m/m CA GDP

- Regime: modest growth
- 68% CI: [+0.15%, +0.45%]
- 95% CI: [+0.00%, +0.60%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.30% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (StatCan monthly GDP is not on FRED
cleanly; StatCan API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 6 (CAD expansion) predictor. CA Monthly GDP released by
StatCan ~60 days after reference month at 08:30 EST (13:30 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 6 CAD trio.

## Caveats

CA Monthly GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 6.1 target: integrate StatCan
`statcan.gc.ca` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 6 CAD predictor. Consensus-only pending StatCan API integration.
