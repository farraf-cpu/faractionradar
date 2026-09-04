# NZ GDP prediction - target 2026-11-05 (T-61)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T23:13:57.014323+00:00

## Final pick

**+5.0%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+4.85%, +5.15%]
- 95% CI: [+4.70%, +5.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +5.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (BPS monthly GDP is not on FRED
cleanly; BPS API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 25 (IDR expansion) predictor. NZ GDP released by
BPS ~16 days after quarter end (early BPS release) at 10:45 IDRT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 25 IDR trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 25.1 target: integrate BPS
`bps.go.id` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 25 IDR predictor. Consensus-only pending BPS API integration.
