# JP CPI prediction - target 2026-10-14 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-14T01:20:56.739300+00:00

## Final pick

**+1.0%** y/y NZ CPI CPI

- Regime: below target
- 68% CI: [+0.85%, +1.15%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.70%, +1.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +1.00% | 0.15pp |

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

- **v1-simple-blend (2026-10-14)** - first ship. Phase 10 CNY expansion. Consensus-only pending NBS NBS Statistical Portal API.
