# CPI prediction — target 2026-09-11 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T00:48:16.574051+00:00

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
| market | +0.00% | 0.12 pp |
| trend | +0.32% | 0.15 pp |

## Method

v1-simple-blend: inverse-MAE-weighted mean of the sub-models above. Weights
are hardcoded from published/estimated MAE benchmarks (consensus 0.08pp,
market 0.12pp, trend 0.15pp). CI is inverse-variance-combined sigma. This
is a Phase 1.5 placeholder — Phase 2 target is a proper Bayesian blend with
Cleveland Fed nowcast + trimmed-mean sub-model + shelter/energy carve-outs.
