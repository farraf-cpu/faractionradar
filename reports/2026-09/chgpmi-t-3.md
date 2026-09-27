# Chicago PMI prediction — target 2026-09-30 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-27T15:46:58.864880+00:00

## Final pick

**49.7** Chicago Business Barometer (0-100 diffusion index)

- Regime: modest regional contraction
- 68% CI: [47.5, 51.9] · sigma source: prior (inverse-MAE)
- 95% CI: [45.3, 54.0]
- Lean vs consensus: below consensus by 1.6 pts
- Sub-models used: consensus, anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 2.50 pts |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 51.3 | 2.5 pts |
| anchor | 47.1 | 4.0 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
MNI Chicago Business Barometer is subscription-only (not on FRED), so no
trend sub-model in v1. Same architecture as ISM Mfg/Svc predictors.

Chicago PMI leads ISM Manufacturing by ~2 business days (releases last
business day of month; ISM Mfg is 1st business day of following month).

## Phase 2 targets

- **National ISM Mfg cross-check** — historical Chicago→ISM correlation is
  ~0.75; use Chicago as a nowcast input to ISM Mfg predictor
- **New Orders sub-index** — Chicago publishes sub-indices; New Orders leads
  headline by 1-2 months

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 22nd event covered.
