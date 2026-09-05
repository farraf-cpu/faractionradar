# BR CPI (IPCA) prediction - target 2026-09-10 (T-5)

**Model version:** `v1.1-sidra`
**Published:** 2026-09-05T00:03:45.125583+00:00

## Final pick

**+4.6%** y/y IPCA (12-mo rolling)

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+4.40%, +4.80%]
- 95% CI: [+4.20%, +5.00%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +4.60% | 0.20pp |

## Method

`v1.1-sidra`: inverse-MAE-weighted blend of FF consensus + SIDRA
IPCA 12-mo y/y 3-mo mean trend. SIDRA (apisidra.ibge.gov.br) is
IBGE's public API — no authentication required, activates
unconditionally when the API is reachable.

## Positioning

Second Phase 15 (BRL expansion) predictor. BCB targets 3% IPCA
y/y (+/- 1.5pp). Released by IBGE ~9-11th of following month at
09:00 BRT.

## Caveats

FRED coverage for Japan CPI is dead — an IBGE IBGE Statistical Portal API integration
(ibge.gov.br, free with registration) would give a real trend
anchor. Phase 15.1 target.

## Change log

- **v1-simple-blend (2026-09-05)** - first ship. Phase 15 BRL expansion. Consensus-only pending IBGE IBGE Statistical Portal API.
