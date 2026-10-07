# Initial Jobless Claims prediction — target 2026-10-08 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-07T20:05:31.166721+00:00

## Final pick

**200K** claims (initial, seasonally adjusted)

- Regime: tight labor market
- 68% CI: [192K, 208K] · sigma source: prior (inverse-MAE)
- 95% CI: [184K, 216K]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 200K | 10K |
| trend | 200K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
