# NZ GDP prediction - target 2026-11-30 (T-86)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:40:39.464738+00:00

## Final pick

**+3.0%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+2.85%, +3.15%]
- 95% CI: [+2.70%, +3.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +3.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (TurkStat monthly GDP is not on FRED
cleanly; TurkStat API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 17 (TRY expansion) predictor. NZ GDP released by
TurkStat ~16 days after quarter end (early TurkStat release) at 10:45 TRYT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 17 TRY trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 17.1 target: integrate TurkStat
`tuik.gov.tr` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 17 TRY predictor. Consensus-only pending TurkStat API integration.
