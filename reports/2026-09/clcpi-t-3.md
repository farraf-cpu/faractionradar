# JP CPI prediction - target 2026-09-08 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T22:27:50.929254+00:00

## Final pick

**+3.5%** y/y NZ CPI CPI

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+3.35%, +3.65%]
- 95% CI: [+3.20%, +3.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +3.50% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 22 (CLP expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by INE ~19th-27th of
following month at 10:45 CLPT.

## Caveats

FRED coverage for Japan CPI is dead — an INE INE Statistical Portal API integration
(ine.gob.cl, free with registration) would give a real trend
anchor. Phase 22.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 22 CLP expansion. Consensus-only pending INE INE Statistical Portal API.
