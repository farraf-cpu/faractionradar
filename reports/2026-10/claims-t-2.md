# Initial Jobless Claims prediction — target 2026-10-15 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-13T20:19:28.414282+00:00

## Final pick

**199K** claims (initial, seasonally adjusted)

- Regime: very tight labor market
- 68% CI: [190K, 207K] · sigma source: prior (inverse-MAE)
- 95% CI: [182K, 215K]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 199K | 10K |
| trend | 198K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
