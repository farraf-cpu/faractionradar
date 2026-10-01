# NFP prediction — target 2026-10-02 (T-1)

**Model version:** `v1.1-bayesian-blend-ladder-dist`
**Published:** 2026-10-01T10:32:18.650203+00:00

## Final pick

**+100K jobs**

- 68% CI: [+69, +131] K · sigma source: prior (blended RMSE)
- 95% CI: [+38, +162] K
- Lean vs consensus: SLIGHTLY ABOVE consensus

## Market outcome distribution (source: `kalshi-ladder`)

| Jobs count | Probability |
|------------|-------------|
| <=25K | 24.5% |
| 25-75K | 15.0% |
| 75-125K | 60.5% **(modal)** |
| 125-175K | 0.0% |
| 175-225K | 0.0% |
| 225K+ | 0.0% |

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| Bloomberg consensus       |     +89 K | ~55 K |
| Prediction markets (avg)  |     +97 K | ~40 K |
| ML ensemble (revised)     |     +36 K | — |
| First-print ensemble      |    +158 K | — |
| Bridge models median      |    +121 K | — |
| Sector decomposition (11) |    +114 K | — |
| Grand median (all models) |    +114 K | — |
| **Blended (Bayesian)**    | **   +100 K** | — |
