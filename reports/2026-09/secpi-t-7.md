# JP CPI prediction - target 2026-09-11 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:26:13.934720+00:00

## Final pick

**+0.5%** y/y NZ CPI CPI

- Regime: below target
- 68% CI: [+0.35%, +0.65%]
- 95% CI: [+0.20%, +0.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.50% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 9 (SEK expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by SCB ~19th-27th of
following month at 10:45 SEKT.

## Caveats

FRED coverage for Japan CPI is dead — an SCB SCB Statistical Portal API integration
(scb.se, free with registration) would give a real trend
anchor. Phase 9.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 9 SEK expansion. Consensus-only pending SCB SCB Statistical Portal API.
