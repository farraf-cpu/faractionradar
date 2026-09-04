# NZ GDP prediction - target 2026-11-30 (T-86)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T22:17:48.686325+00:00

## Final pick

**+0.7%** q/q NZ GDP

- Regime: solid monthly expansion
- 68% CI: [+0.55%, +0.85%]
- 95% CI: [+0.40%, +1.00%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.70% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (GUS monthly GDP is not on FRED
cleanly; GUS API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 21 (PLN expansion) predictor. NZ GDP released by
GUS ~16 days after quarter end (early GUS release) at 10:45 PLNT (12:00 UTC). Sits alongside
BoE Bank Rate + CA CPI in Phase 21 PLN trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 21.1 target: integrate GUS
`stat.gov.pl` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 21 PLN predictor. Consensus-only pending GUS API integration.
