# NZ GDP prediction - target 2026-10-24 (T-50)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:53:48.843918+00:00

## Final pick

**+1.4%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+1.25%, +1.55%]
- 95% CI: [+1.10%, +1.70%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +1.40% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (BOK monthly GDP is not on FRED
cleanly; BOK API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 12 (KRW expansion) predictor. NZ GDP released by
BOK ~16 days after quarter end (early BOK release) at 10:45 KRWT (23:00 UTC prior day). Sits alongside
BoE Bank Rate + CA CPI in Phase 12 KRW trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 12.1 target: integrate BOK
`kosis.kr` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 12 KRW predictor. Consensus-only pending BOK API integration.
