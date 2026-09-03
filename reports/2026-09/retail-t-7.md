# Retail Sales prediction — target 2026-09-16 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T10:34:58.441276+00:00

## Final pick

**+0.7% m/m** (Advance Retail Sales, headline)

- 68% CI: [+0.25%, +1.05%]
- 95% CI: [-0.15%, +1.45%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30 pp |
| trend | +0.65% | 0.40 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (0.30pp) + FRED
RSXFS 6-mo trend (0.40pp). Retail sales is one of the noisier monthly prints
— consumer spending swings sharply on weather, holiday timing, and one-off
sector moves. Consensus MAE wider than inflation prints; blend MAE follows.

Phase 2 target: add auto-sales adjustment sub-model (Ward's Intelligence
publishes monthly auto SAAR ahead of the Census release — leads headline
by ~5-7 days) + gas station sales carve-out (retail food services excludes
gas but headline includes it, so oil-price shocks flow through).
