# CPI prediction — target 2026-10-14 (T-0)

**Model version:** `v1.3-kalshi-ladder-dist`
**Published:** 2026-10-14T15:21:54.035370+00:00

## Final pick

**+0.6% m/m**

- 68% CI: [+0.59%, +0.71%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.52%, +0.77%]
- Lean vs consensus: above consensus by 0.05pp
- Sub-models used: consensus, market, trend


## Market outcome distribution (source: `kalshi-ladder`)

| CPI m/m | Probability |
|---------|-------------|
| -0.1% | 0.5% |
| 0.0% | 0.0% |
| +0.1% | 0.5% |
| +0.2% | 0.0% |
| +0.3% | 9.5% |
| +0.4% | 18.0% |
| +0.5% | 71.5% **(modal)** |

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.60% | 0.08 pp |
| cleveland_fed | — | 0.06 pp |
| market | +1.00% | 0.12 pp |
| trimmed_mean | — | 0.10 pp |
| trend | +0.30% | 0.15 pp |

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
