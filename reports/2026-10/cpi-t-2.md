# CPI prediction — target 2026-10-14 (T-2)

**Model version:** `v1.3-kalshi-ladder-dist`
**Published:** 2026-10-12T21:58:54.584399+00:00

## Final pick

**+0.7% m/m**

- 68% CI: [+0.59%, +0.72%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.53%, +0.78%]
- Lean vs consensus: above consensus by 0.06pp
- Sub-models used: consensus, market, trend


## Market outcome distribution (source: `kalshi-ladder`)

| CPI m/m | Probability |
|---------|-------------|
| -0.1% | 0.5% |
| 0.0% | 0.0% |
| +0.1% | 1.0% |
| +0.2% | 1.0% |
| +0.3% | 6.0% |
| +0.4% | 33.0% |
| +0.5% | 58.5% **(modal)** |

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.60% | 0.08 pp |
| cleveland_fed | — | 0.06 pp |
| market | +1.00% | 0.12 pp |
| trimmed_mean | — | 0.10 pp |
| trend | +0.34% | 0.15 pp |

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
