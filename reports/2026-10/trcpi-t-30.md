# JP CPI prediction - target 2026-10-05 (T-30)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:40:38.796409+00:00

## Final pick

**+30.0%** y/y NZ CPI CPI

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+29.85%, +30.15%]
- 95% CI: [+29.70%, +30.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +30.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 17 (TRY expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by TurkStat ~19th-27th of
following month at 10:45 TRYT.

## Caveats

FRED coverage for Japan CPI is dead — an TurkStat TurkStat Statistical Portal API integration
(tuik.gov.tr, free with registration) would give a real trend
anchor. Phase 17.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 17 TRY expansion. Consensus-only pending TurkStat TurkStat Statistical Portal API.
