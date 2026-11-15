# JP CPI prediction - target 2026-10-21 (T-47)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:06:06.132435+00:00

## Final pick

**+2.4%** y/y NZ CPI CPI

- Regime: above RBNZ target
- 68% CI: [+2.25%, +2.55%]
- 95% CI: [+2.10%, +2.70%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.40% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 7 (NZD expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by StatsNZ ~19th-27th of
following month at 10:45 NZDT.

## Caveats

FRED coverage for Japan CPI is dead — an StatsNZ Infoshare API integration
(nzdotstat.stats.govt.nz, free with registration) would give a real trend
anchor. Phase 7.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 7 NZD expansion. Consensus-only pending StatsNZ Infoshare API.
