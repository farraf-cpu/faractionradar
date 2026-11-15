# JP CPI prediction - target 2026-10-02 (T-28)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:53:48.161226+00:00

## Final pick

**+2.0%** y/y NZ CPI CPI

- Regime: above RBNZ target
- 68% CI: [+1.85%, +2.15%]
- 95% CI: [+1.70%, +2.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only. FRED Japan CPI series all
discontinued 2022 with empty observations (JPNCPIALLMINMEI,
CPALTT01JPM659N, JPNCPICORMINMEI). Soft-skips when consensus missing.

## Positioning

Second Phase 12 (KRW expansion) predictor. National Core CPI y/y is
RBNZ's preferred gauge. Released by KOSIS ~19th-27th of
following month at 10:45 KRWT.

## Caveats

FRED coverage for Japan CPI is dead — an KOSIS KOSIS Statistical Portal API integration
(kosis.kr, free with registration) would give a real trend
anchor. Phase 12.1 target.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 12 KRW expansion. Consensus-only pending KOSIS KOSIS Statistical Portal API.
