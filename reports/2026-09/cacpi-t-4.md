# CA CPI prediction - target 2026-09-16 (T-4)

**Model version:** `v1.1-statcan`
**Published:** 2026-09-12T22:10:49.287495+00:00

## Final pick

**+2.7%** y/y CA CPI

- Regime: upper end of BOC band
- 68% CI: [+2.47%, +2.87%] · sigma source: prior (inverse-MAE)
- 95% CI: [+2.27%, +3.07%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.20 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +2.67% | 0.20pp |

## Method

`v1.1-statcan`: inverse-MAE-weighted mean of FF consensus + StatCan
WDS API (apisidra-like: vector v108785713 for CPI y/y all-items).
No key required — StatCan WDS is public.

## Positioning

Second Phase 6 CAD predictor. CA CPI released monthly by StatCan
~3 weeks after reference month at 08:30 EST. BOC target 2% CPI y/y
(1-3% band).

## Change log

- **v1.1-statcan (2026-09-12)** - swapped stale FRED trend for live StatCan WDS API. Auto-active.
- **v1-simple-blend (2026-09-04)** - first ship. Phase 6 CAD expansion.
