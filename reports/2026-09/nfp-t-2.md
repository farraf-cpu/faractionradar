# NFP prediction — target 2026-09-04 (T-2)

**Model version:** `v1-bayesian-blend`
**Published:** 2026-09-02T14:15:48.508926+00:00

## Final pick

**+80K jobs**

- 68% CI: [+50, +111] K
- 95% CI: [+19, +142] K
- Lean vs consensus: MODESTLY ABOVE consensus

## Caveats

The prediction-markets input is a hardcoded July baseline pending Kalshi ticker-mapping verification (Phase 1.5). Consensus is live from ForexFactory; the point estimate is anchored to live consensus + first-print model output. The markets weight will refresh once real ticker mapping lands.

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| Bloomberg consensus       |     +55 K | ~55 K |
| Prediction markets (avg)  |     +82 K (stale, see caveat) | ~40 K |
| ML ensemble (revised)     |     +20 K | — |
| First-print ensemble      |    +166 K | — |
| Bridge models median      |    +109 K | — |
| Sector decomposition (11) |    +109 K | — |
| Grand median (all models) |     +94 K | — |
| **Blended (Bayesian)**    | **    +80 K** | — |
