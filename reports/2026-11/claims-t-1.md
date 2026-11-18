# Initial Jobless Claims prediction — target 2026-11-19 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-18T22:14:17.551091+00:00

## Final pick

**197K** claims (initial, seasonally adjusted)

- Regime: very tight labor market
- 68% CI: [189K, 205K] · sigma source: prior (inverse-MAE)
- 95% CI: [180K, 213K]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 198K | 10K |
| trend | 195K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
