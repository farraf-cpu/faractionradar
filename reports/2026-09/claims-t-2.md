# Initial Jobless Claims prediction — target 2026-09-10 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-08T10:42:13.967902+00:00

## Final pick

**206K** claims (initial, seasonally adjusted)

- Regime: tight labor market
- 68% CI: [198K, 214K] · sigma source: prior (inverse-MAE)
- 95% CI: [189K, 222K]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 10.0 K |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 205K | 10K |
| trend | 207K | 14K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~10K MAE) + FRED
ICSA 4-week trend (~14K MAE). Claims is a weekly release, so the trend is
much more current than for monthly events.

Phase 2 target: seasonal adjustment overlay (Labor Day / MLK Day / July 4th
weeks routinely produce +30-50K spikes that seasonally-adjusted series
under-adjusts for). Also SAHM Rule cross-check — if trend is turning up
sharply, flag on report.
