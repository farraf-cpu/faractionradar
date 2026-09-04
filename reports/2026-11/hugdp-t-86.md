# NZ GDP prediction - target 2026-11-30 (T-86)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T22:09:30.311272+00:00

## Final pick

**+0.5%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+0.35%, +0.65%]
- 95% CI: [+0.20%, +0.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.50% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (KSH monthly GDP is not on FRED
cleanly; KSH API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 20 (HUF expansion) predictor. NZ GDP released by
KSH ~16 days after quarter end (early KSH release) at 10:45 HUFT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 20 HUF trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 20.1 target: integrate KSH
`ksh.hu` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 20 HUF predictor. Consensus-only pending KSH API integration.
