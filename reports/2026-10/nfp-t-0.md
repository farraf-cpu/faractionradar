# NFP prediction — target 2026-10-02 (T-0)

**Model version:** `v1.1-bayesian-blend-ladder-dist`
**Published:** 2026-10-02T14:18:02.134426+00:00

## Final pick

**+35K jobs**

- 68% CI: [+4, +66] K · sigma source: prior (blended RMSE)
- 95% CI: [-27, +97] K
- Lean vs consensus: MODESTLY BELOW consensus

## Market outcome distribution (source: `kalshi-ladder`)

| Jobs count | Probability |
|------------|-------------|
| <=25K | 50.0% **(modal)** |
| 25-75K | 0.0% |
| 75-125K | 50.0% |
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
| Prediction markets (avg)  |     -12 K | ~40 K |
| ML ensemble (revised)     |     +32 K | — |
| First-print ensemble      |    +165 K | — |
| Bridge models median      |    +114 K | — |
| Sector decomposition (11) |    +114 K | — |
| Grand median (all models) |    +108 K | — |
| **Blended (Bayesian)**    | **    +35 K** | — |
