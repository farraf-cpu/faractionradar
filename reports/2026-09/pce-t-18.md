# PCE prediction — target 2026-09-22 (T-18)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-04T10:10:57.723185+00:00

## Final pick

**+0.2% m/m** (PCE Price Index)

- 68% CI: [+0.15%, +0.23%]
- 95% CI: [+0.11%, +0.27%]
- Lean vs consensus: no consensus
- Sub-models used: cleveland_fed, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.05 pp |
| cleveland_fed | +0.13% | 0.04 pp |
| trend | +0.34% | 0.10 pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of consensus (0.05pp) +
Cleveland Fed daily nowcast (0.04pp; when PCE cycle active) + FRED
PCEPI 6-mo m/m trend (0.10pp). Consensus MAE on PCE is tighter than
CPI/PPI because it's the Fed's target — analysts scrutinize it more.

Phase 2 target adds Core PCE decomposition and splits headline vs
core into separate slugs (pce-<date> vs pce-core-<date>).
