# JP CPI prediction - target 2026-09-12 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:14:09.913488+00:00

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

Second Phase 14 (INR expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by MoSPI ~19th-27th of
following month at 10:45 INRT.

## Caveats

FRED coverage for Japan CPI is dead — an MoSPI MoSPI Statistical Portal API integration
(mospi.gov.in, free with registration) would give a real trend
anchor. Phase 14.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 14 INR expansion. Consensus-only pending MoSPI MoSPI Statistical Portal API.
