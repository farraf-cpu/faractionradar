# JP CPI prediction - target 2026-09-10 (T-5)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T21:22:51.282239+00:00

## Final pick

**+5.0%** y/y NZ CPI CPI

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+4.85%, +5.15%]
- 95% CI: [+4.70%, +5.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +5.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 15 (BRL expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by IBGE ~19th-27th of
following month at 10:45 BRLT.

## Caveats

FRED coverage for Japan CPI is dead — an IBGE IBGE Statistical Portal API integration
(ibge.gov.br, free with registration) would give a real trend
anchor. Phase 15.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 15 BRL expansion. Consensus-only pending IBGE IBGE Statistical Portal API.
