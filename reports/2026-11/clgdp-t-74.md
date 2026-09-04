# NZ GDP prediction - target 2026-11-18 (T-74)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T22:27:51.608290+00:00

## Final pick

**+0.8%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+0.65%, +0.95%]
- 95% CI: [+0.50%, +1.10%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.80% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (Banco Central de Chile monthly GDP is not on FRED
cleanly; Banco Central de Chile API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 22 (CLP expansion) predictor. NZ GDP released by
Banco Central de Chile ~16 days after quarter end (early Banco Central de Chile release) at 10:45 CLPT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 22 CLP trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 22.1 target: integrate Banco Central de Chile
`bcentral.cl` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 22 CLP predictor. Consensus-only pending Banco Central de Chile API integration.
