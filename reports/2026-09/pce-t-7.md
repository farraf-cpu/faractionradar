# PCE prediction — target 2026-09-22 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T10:14:42.086666+00:00

## Final pick

**+0.3% m/m** (PCE Price Index)

- 68% CI: [+0.24%, +0.44%]
- 95% CI: [+0.14%, +0.54%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.05 pp |
| trend | +0.34% | 0.10 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (0.05pp) + FRED
PCEPI 6-mo m/m trend (0.10pp). Blended sigma is the inverse-variance
combination. Consensus MAE on PCE is tighter than CPI/PPI because it's the
Fed's target — analysts scrutinize it more.

Phase 2 target adds Cleveland Fed nowcast + Core PCE decomposition and
splits headline vs core into separate slugs (pce-<date> vs pce-core-<date>).
