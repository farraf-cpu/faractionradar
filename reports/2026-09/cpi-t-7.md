# CPI prediction — target 2026-09-11 (T-7)

**Model version:** `v1.2-simple-blend`
**Published:** 2026-09-04T10:06:47.371076+00:00

## Final pick

**+0.1% m/m**

- 68% CI: [+0.05%, +0.23%]
- 95% CI: [-0.05%, +0.33%]
- Lean vs consensus: no consensus
- Sub-models used: market, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.08 pp |
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
