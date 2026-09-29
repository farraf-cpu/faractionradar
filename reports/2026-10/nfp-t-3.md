# NFP prediction — target 2026-10-02 (T-3)

**Model version:** `v1.1-bayesian-blend-ladder-dist`
**Published:** 2026-09-29T14:17:35.045401+00:00

## Final pick

**+100K jobs**

- 68% CI: [+69, +131] K · sigma source: prior (blended RMSE)
- 95% CI: [+38, +162] K
- Lean vs consensus: SLIGHTLY ABOVE consensus

## Market outcome distribution (source: `kalshi-ladder`)

| Jobs count | Probability |
|------------|-------------|
| <=25K | 18.5% |
| 25-75K | 18.0% |
| 75-125K | 63.5% **(modal)** |
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
| Bloomberg consensus       |     +90 K | ~55 K |
| Prediction markets (avg)  |     +97 K | ~40 K |
| ML ensemble (revised)     |     +33 K | — |
| First-print ensemble      |    +162 K | — |
| Bridge models median      |    +121 K | — |
| Sector decomposition (11) |    +114 K | — |
| Grand median (all models) |    +118 K | — |
| **Blended (Bayesian)**    | **   +100 K** | — |
