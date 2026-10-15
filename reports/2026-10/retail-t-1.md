# Retail Sales prediction — target 2026-10-16 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-15T15:14:33.675629+00:00

## Final pick

**+0.5% m/m** (Advance Retail Sales, headline)

- 68% CI: [+0.13%, +0.93%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.27%, +1.33%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30 pp |
| trend | +0.53% | 0.40 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (0.30pp) + FRED
RSXFS 6-mo trend (0.40pp). Retail sales is one of the noisier monthly prints
— consumer spending swings sharply on weather, holiday timing, and one-off
sector moves. Consensus MAE wider than inflation prints; blend MAE follows.

Phase 2 target: add auto-sales adjustment sub-model (Ward's Intelligence
publishes monthly auto SAAR ahead of the Census release — leads headline
by ~5-7 days) + gas station sales carve-out (retail food services excludes
gas but headline includes it, so oil-price shocks flow through).
