# UK Monthly GDP prediction - target 2026-09-11 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-07T18:26:49.969242+00:00

## Final pick

**+0.0%** m/m UK GDP

- Regime: flat / stall
- 68% CI: [-0.15%, +0.15%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.30%, +0.30%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.00% | 0.15pp |

## Method

`v1-simple-blend`: consensus-only (ONS Monthly GDP is not on FRED
cleanly; ONS API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 3 (GBP expansion) predictor. UK Monthly GDP released by
ONS ~40 days after reference month at 07:00 UK time. Sits alongside
BoE Bank Rate + UK CPI in Phase 3 GBP trio.

## Caveats

UK Monthly GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 3.1 target: integrate ONS
`api.ons.gov.uk` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend (2026-09-07)** - first ship. Third Phase 3 GBP predictor. Consensus-only pending ONS API integration.
