# NZ GDP prediction - target 2026-11-16 (T-72)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:52:00.946120+00:00

## Final pick

**+0.6%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+0.45%, +0.75%]
- 95% CI: [+0.30%, +0.90%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.60% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (CBS monthly GDP is not on FRED
cleanly; CBS API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 18 (ILS expansion) predictor. NZ GDP released by
CBS ~16 days after quarter end (early CBS release) at 10:45 ILST (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 18 ILS trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 18.1 target: integrate CBS
`cbs.gov.il` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 18 ILS predictor. Consensus-only pending CBS API integration.
