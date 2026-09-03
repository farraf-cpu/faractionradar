# PPI prediction — target 2026-09-10 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T14:21:09.737660+00:00

## Final pick

**+0.4% m/m** (Producer Price Index, Final Demand)

- 68% CI: [+0.29%, +0.59%]
- 95% CI: [+0.14%, +0.74%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.10 pp |
| trend | +0.44% | 0.15 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of up to 2 sub-models. Consensus
(0.10pp historical MAE) + FRED PPIFIS 6-mo m/m trend (0.15pp). Blended sigma
is the inverse-variance combination.

PPI has no Kalshi contract market (as of 2026-09-03) so no prediction-market
sub-model — this makes v1 simpler than CPI. Phase 2 target adds a
sector-decomposition sub-model (energy / food / trade services) since PPI
is more sector-heterogeneous than CPI headline.
