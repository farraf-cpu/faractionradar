# PPI prediction — target 2026-10-15 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-08T19:50:42.867798+00:00

## Final pick

**+0.4% m/m** (Producer Price Index, Final Demand)

- 68% CI: [+0.28%, +0.49%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.17%, +0.60%]
- Lean vs consensus: no consensus
- Sub-models used: trend, core_anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.10 pp |
| trend | +0.45% | 0.15 pp |
| core_anchor | +0.32% | 0.15 pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 3 sub-models —
consensus (0.10pp) + FRED PPIFIS 6-mo m/m trend (0.15pp) + FRED WPSFD4131
6-mo m/m trend (0.15pp, PPI Finished Goods ex food/energy). The
core-goods anchor signals whether the headline print is being driven by
transitory food/energy swings (divergence) or persistent underlying
pressure (convergence). Blended sigma is the inverse-variance combination.

PPI has no Kalshi contract market (as of 2026-09-03) so no prediction-market
sub-model. Phase 2 target: energy carve-out (WPUFD42) + food carve-out
(WPUFD41) for finer decomposition when component data warrants.
