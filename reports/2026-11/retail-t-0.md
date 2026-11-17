# Retail Sales prediction — target 2026-11-17 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-17T19:17:32.088322+00:00

## Final pick

**+0.3% m/m** (Advance Retail Sales, headline)

- 68% CI: [+0.04%, +0.52%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.20%, +0.77%]
- Lean vs consensus: above consensus by 0.18pp
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.10% | 0.30 pp |
| trend | +0.52% | 0.40 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (0.30pp) + FRED
RSXFS 6-mo trend (0.40pp). Retail sales is one of the noisier monthly prints
— consumer spending swings sharply on weather, holiday timing, and one-off
sector moves. Consensus MAE wider than inflation prints; blend MAE follows.

Phase 2 target: add auto-sales adjustment sub-model (Ward's Intelligence
publishes monthly auto SAAR ahead of the Census release — leads headline
by ~5-7 days) + gas station sales carve-out (retail food services excludes
gas but headline includes it, so oil-price shocks flow through).
