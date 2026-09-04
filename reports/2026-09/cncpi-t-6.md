# JP CPI prediction - target 2026-09-10 (T-6)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:34:46.285454+00:00

## Final pick

**-0.1%** y/y NZ CPI CPI

- Regime: deflationary / disinflation
- 68% CI: [-0.25%, +0.05%]
- 95% CI: [-0.40%, +0.20%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | -0.10% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 10 (CNY expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by NBS ~19th-27th of
following month at 10:45 CNYT.

## Caveats

FRED coverage for Japan CPI is dead — an NBS NBS Statistical Portal API integration
(stats.gov.cn, free with registration) would give a real trend
anchor. Phase 10.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 10 CNY expansion. Consensus-only pending NBS NBS Statistical Portal API.
