# Initial Jobless Claims prediction — target 2026-11-26 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-24T01:48:18.901672+00:00

## Final pick

**198K** claims (initial, seasonally adjusted)

- Regime: very tight labor market
- 68% CI: [184K, 212K] · sigma source: prior (inverse-MAE)
- 95% CI: [170K, 226K]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 10K |
| trend | 198K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
