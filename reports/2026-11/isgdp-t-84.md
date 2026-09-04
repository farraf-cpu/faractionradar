# NZ GDP prediction - target 2026-11-28 (T-84)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T23:12:53.698790+00:00

## Final pick

**+0.3%** q/q NZ GDP

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

`v1-simple-blend`: consensus-only (Statistics Iceland monthly GDP is not on FRED
cleanly; Statistics Iceland API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 24 (ISK expansion) predictor. NZ GDP released by
Statistics Iceland ~16 days after quarter end (early Statistics Iceland release) at 10:45 ISKT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 24 ISK trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 24.1 target: integrate Statistics Iceland
`hagstofa.is` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 24 ISK predictor. Consensus-only pending Statistics Iceland API integration.
