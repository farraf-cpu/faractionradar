# NZ GDP prediction - target 2026-11-30 (T-86)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T23:12:02.919704+00:00

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

`v1-simple-blend`: consensus-only (DST monthly GDP is not on FRED
cleanly; DST API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 23 (DKK expansion) predictor. NZ GDP released by
DST ~16 days after quarter end (early DST release) at 10:45 DKKT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 23 DKK trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 23.1 target: integrate DST
`dst.dk` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 23 DKK predictor. Consensus-only pending DST API integration.
