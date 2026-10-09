# Retail Sales prediction — target 2026-10-16 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-09T19:35:33.886300+00:00

## Final pick

**+0.7% m/m** (Advance Retail Sales, headline)

- 68% CI: [+0.29%, +1.09%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.11%, +1.49%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.40 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30 pp |
| trend | +0.69% | 0.40 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (0.30pp) + FRED
RSXFS 6-mo trend (0.40pp). Retail sales is one of the noisier monthly prints
— consumer spending swings sharply on weather, holiday timing, and one-off
sector moves. Consensus MAE wider than inflation prints; blend MAE follows.

Phase 2 target: add auto-sales adjustment sub-model (Ward's Intelligence
publishes monthly auto SAAR ahead of the Census release — leads headline
by ~5-7 days) + gas station sales carve-out (retail food services excludes
gas but headline includes it, so oil-price shocks flow through).
