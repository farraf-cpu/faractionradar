# NZ GDP prediction - target 2026-11-28 (T-84)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:14:10.601415+00:00

## Final pick

**+6.5%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+6.35%, +6.65%]
- 95% CI: [+6.20%, +6.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +6.50% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (MoSPI monthly GDP is not on FRED
cleanly; MoSPI API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 14 (INR expansion) predictor. NZ GDP released by
MoSPI ~16 days after quarter end (early MoSPI release) at 10:45 INRT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 14 INR trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 14.1 target: integrate MoSPI
`mospi.gov.in` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 14 INR predictor. Consensus-only pending MoSPI API integration.
