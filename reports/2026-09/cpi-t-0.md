# CPI prediction — target 2026-09-11 (T-0)

**Model version:** `v1.3-kalshi-ladder-dist`
**Published:** 2026-09-11T10:41:22.555656+00:00

## Final pick

**+0.3% m/m**

- 68% CI: [+0.20%, +0.32%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.13%, +0.38%]
- Lean vs consensus: below consensus by 0.14pp
- Sub-models used: consensus, market, trend


## Market outcome distribution (source: `kalshi-ladder`)

| CPI m/m | Probability |
|---------|-------------|
| -0.1% | 0.5% |
| 0.0% | 0.5% |
| +0.1% | 5.5% |
| +0.2% | 37.5% |
| +0.3% | 45.5% **(modal)** |
| +0.4% | 8.0% |
| +0.5% | 2.5% |


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.08 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.40% | 0.08 pp |
| cleveland_fed | — | 0.06 pp |
| market | +0.00% | 0.12 pp |
| trimmed_mean | — | 0.10 pp |
| trend | +0.32% | 0.15 pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 4 sub-models.
Consensus + Kalshi market + FRED trimmed-mean CPI + FRED CPIAUCSL 6-mo
trend. Weights are `1 / MAE`, so tighter historical sources dominate.
CI is inverse-variance-combined sigma. `TRMMEANCPIM159SFRBDAL` (Dallas
Fed 8% trimmed mean m/m) added in v1.1 as a mean-reverting anchor that
excludes the top + bottom 8% of price change tails — historically
forecasts headline m/m with ~0.10pp MAE.

Phase 2 target adds Cleveland Fed nowcast + shelter/energy carve-outs
and restructures as a proper Bayesian blend with regime-aware weights.
