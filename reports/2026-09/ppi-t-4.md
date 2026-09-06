# PPI prediction — target 2026-09-10 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-06T10:37:09.179793+00:00

## Final pick

**+0.4% m/m** (Producer Price Index, Final Demand)

- 68% CI: [+0.33%, +0.50%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.25%, +0.59%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.10 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate vs consensus | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.40% | 0.10 pp |
| trend | +0.44% | 0.15 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of up to 2 sub-models. Consensus
(0.10pp historical MAE) + FRED PPIFIS 6-mo m/m trend (0.15pp). Blended sigma
is the inverse-variance combination.

PPI has no Kalshi contract market (as of 2026-09-03) so no prediction-market
sub-model — this makes v1 simpler than CPI. Phase 2 target adds a
sector-decomposition sub-model (energy / food / trade services) since PPI
is more sector-heterogeneous than CPI headline.
