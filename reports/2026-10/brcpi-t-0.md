# BR CPI (IPCA) prediction - target 2026-10-09 (T-0)

**Model version:** `v1.1-sidra`
**Published:** 2026-10-09T22:39:25.348435+00:00

## Final pick

**+4.4%** y/y IPCA (12-mo rolling)

- Regime: hot JP inflation (RBNZ hawkish pressure)
- 68% CI: [+4.21%, +4.61%] · sigma source: prior (inverse-MAE)
- 95% CI: [+4.01%, +4.81%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +4.41% | 0.20pp |

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

- **v1-simple-blend (2026-10-09)** - first ship. Phase 15 BRL expansion. Consensus-only pending IBGE IBGE Statistical Portal API.
