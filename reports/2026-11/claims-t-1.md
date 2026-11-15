# Initial Jobless Claims prediction — target 2026-11-12 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-11T21:35:36.533567+00:00

## Final pick

**194K** claims (initial, seasonally adjusted)

- Regime: very tight labor market
- 68% CI: [186K, 203K] · sigma source: prior (inverse-MAE)
- 95% CI: [178K, 211K]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 194K | 10K |
| trend | 195K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
