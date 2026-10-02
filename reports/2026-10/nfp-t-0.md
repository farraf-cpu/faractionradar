# NFP prediction — target 2026-10-02 (T-0)

**Model version:** `v1.1-bayesian-blend-ladder-dist`
**Published:** 2026-10-02T10:31:07.922913+00:00

## Final pick

**+98K jobs**

- 68% CI: [+67, +129] K · sigma source: prior (blended RMSE)
- 95% CI: [+36, +160] K
- Lean vs consensus: SLIGHTLY ABOVE consensus

## Market outcome distribution (source: `kalshi-ladder`)

| Jobs count | Probability |
|------------|-------------|
| <=25K | 23.5% |
| 25-75K | 18.0% |
| 75-125K | 58.5% **(modal)** |
| 125-175K | 0.0% |
| 175-225K | 0.0% |
| 225K+ | 0.0% |



## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | ~40 K (best sub-model, markets) |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| Bloomberg consensus       |     +89 K | ~55 K |
| Prediction markets (avg)  |     +95 K | ~40 K |
| ML ensemble (revised)     |     +39 K | — |
| First-print ensemble      |    +158 K | — |
| Bridge models median      |    +121 K | — |
| Sector decomposition (11) |    +113 K | — |
| Grand median (all models) |    +114 K | — |
| **Blended (Bayesian)**    | **    +98 K** | — |
