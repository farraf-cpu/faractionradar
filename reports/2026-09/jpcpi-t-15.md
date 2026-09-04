# JP CPI prediction - target 2026-09-19 (T-15)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T17:26:15.939990+00:00

## Final pick

**+2.7%** y/y JP National Core CPI

- Regime: above BOJ target
- 68% CI: [+2.55%, +2.85%]
- 95% CI: [+2.40%, +3.00%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.70% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 4 (JPY expansion) predictor. National Core CPI y/y is
BOJ's preferred inflation gauge. Released by MIC ~19th-27th of
following month at 08:30 JST.

## Caveats

FRED coverage for Japan CPI is dead — an e-Stat API integration
(api.e-stat.go.jp, free with registration) would give a real trend
anchor. Phase 4.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 4 JPY expansion. Consensus-only pending e-Stat API.
