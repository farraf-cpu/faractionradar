# JP CPI prediction - target 2026-10-01 (T-26)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T23:13:56.312594+00:00

## Final pick

**+2.5%** y/y NZ CPI CPI

- Regime: above RBNZ target
- 68% CI: [+2.35%, +2.65%]
- 95% CI: [+2.20%, +2.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.50% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 25 (IDR expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by BPS ~19th-27th of
following month at 10:45 IDRT.

## Caveats

FRED coverage for Japan CPI is dead — an BPS BPS Statistical Portal API integration
(bps.go.id, free with registration) would give a real trend
anchor. Phase 25.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 25 IDR expansion. Consensus-only pending BPS BPS Statistical Portal API.
