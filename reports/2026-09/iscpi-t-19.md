# JP CPI prediction - target 2026-09-24 (T-19)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T23:12:52.985305+00:00

## Final pick

**+4.0%** y/y NZ CPI CPI

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+3.85%, +4.15%]
- 95% CI: [+3.70%, +4.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +4.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 24 (ISK expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by Statistics Iceland ~19th-27th of
following month at 10:45 ISKT.

## Caveats

FRED coverage for Japan CPI is dead — an Statistics Iceland Statistics Iceland Statistical Portal API integration
(hagstofa.is, free with registration) would give a real trend
anchor. Phase 24.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 24 ISK expansion. Consensus-only pending Statistics Iceland Statistics Iceland Statistical Portal API.
