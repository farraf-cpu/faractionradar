# JP CPI prediction - target 2026-09-10 (T-5)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T23:12:02.224029+00:00

## Final pick

**+1.6%** y/y NZ CPI CPI

- Regime: near RBNZ target
- 68% CI: [+1.45%, +1.75%]
- 95% CI: [+1.30%, +1.90%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +1.60% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 23 (DKK expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by DST ~19th-27th of
following month at 10:45 DKKT.

## Caveats

FRED coverage for Japan CPI is dead — an DST DST Statistical Portal API integration
(dst.dk, free with registration) would give a real trend
anchor. Phase 23.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 23 DKK expansion. Consensus-only pending DST DST Statistical Portal API.
