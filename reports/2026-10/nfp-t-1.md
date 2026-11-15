# NFP prediction — target 2026-10-02 (T-1)

**Model version:** `v1.1-bayesian-blend-ladder-dist`
**Published:** 2026-10-01T14:18:51.511206+00:00

## Final pick

**+99K jobs**

- 68% CI: [+68, +130] K · sigma source: prior (blended RMSE)
- 95% CI: [+37, +161] K
- Lean vs consensus: SLIGHTLY ABOVE consensus

## Market outcome distribution (source: `kalshi-ladder`)

| Jobs count | Probability |
|------------|-------------|
| <=25K | 23.0% |
| 25-75K | 15.5% |
| 75-125K | 61.5% **(modal)** |
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
| Prediction markets (avg)  |     +96 K | ~40 K |
| ML ensemble (revised)     |     +39 K | — |
| First-print ensemble      |    +158 K | — |
| Bridge models median      |    +121 K | — |
| Sector decomposition (11) |    +114 K | — |
| Grand median (all models) |    +114 K | — |
| **Blended (Bayesian)**    | **    +99 K** | — |
