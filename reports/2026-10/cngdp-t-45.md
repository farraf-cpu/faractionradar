# NZ GDP prediction - target 2026-10-19 (T-45)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:34:46.992230+00:00

## Final pick

**+4.8%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+4.65%, +4.95%]
- 95% CI: [+4.50%, +5.10%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +4.80% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (NBS monthly GDP is not on FRED
cleanly; NBS API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 10 (CNY expansion) predictor. NZ GDP released by
NBS ~16 days after quarter end (early NBS release) at 10:45 CNYT (02:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 10 CNY trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 10.1 target: integrate NBS
`data.stats.gov.cn` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 10 CNY predictor. Consensus-only pending NBS API integration.
