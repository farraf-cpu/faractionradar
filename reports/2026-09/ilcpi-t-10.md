# JP CPI prediction - target 2026-09-15 (T-10)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:52:00.278040+00:00

## Final pick

**+3.0%** y/y NZ CPI CPI

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+2.85%, +3.15%]
- 95% CI: [+2.70%, +3.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +3.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 18 (ILS expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by CBS ~19th-27th of
following month at 10:45 ILST.

## Caveats

FRED coverage for Japan CPI is dead — an CBS CBS Statistical Portal API integration
(cbs.gov.il, free with registration) would give a real trend
anchor. Phase 18.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 18 ILS expansion. Consensus-only pending CBS CBS Statistical Portal API.
