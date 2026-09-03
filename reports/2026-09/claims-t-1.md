# Initial Jobless Claims prediction — target 2026-09-10 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T11:46:01.834546+00:00

## Final pick

**206K** claims (initial, seasonally adjusted)

- Regime: tight labor market
- 68% CI: [192K, 220K]
- 95% CI: [178K, 234K]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 10K |
| trend | 206K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
