# PCE prediction — target 2026-09-22 (T-7)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-15T14:30:13.177203+00:00

## Final pick

**+0.1% m/m** (PCE Price Index)

- 68% CI: [+0.09%, +0.17%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.05%, +0.21%]
- Lean vs consensus: no consensus
- Sub-models used: cleveland_fed


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.04 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.05 pp |
| cleveland_fed | +0.13% | 0.04 pp |
| trend | — | 0.10 pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of consensus (0.05pp) +
Cleveland Fed daily nowcast (0.04pp; when PCE cycle active) + FRED
PCEPI 6-mo m/m trend (0.10pp). Consensus MAE on PCE is tighter than
CPI/PPI because it's the Fed's target — analysts scrutinize it more.

Phase 2 target adds Core PCE decomposition and splits headline vs
core into separate slugs (pce-<date> vs pce-core-<date>).
