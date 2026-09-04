# NZ GDP prediction - target 2026-11-30 (T-86)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:22:51.921307+00:00

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

`v1-simple-blend`: consensus-only (IBGE monthly GDP is not on FRED
cleanly; IBGE API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 15 (BRL expansion) predictor. NZ GDP released by
IBGE ~16 days after quarter end (early IBGE release) at 10:45 BRLT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 15 BRL trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 15.1 target: integrate IBGE
`ibge.gov.br` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 15 BRL predictor. Consensus-only pending IBGE API integration.
