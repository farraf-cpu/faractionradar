# ISM Services PMI prediction — target 2026-10-05 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-04T16:01:32.889430+00:00

## Final pick

**55.2** (diffusion index; 50 = expansion threshold)

- Regime: solid expansion
- 68% CI: [54.1, 56.3] · sigma source: prior (inverse-MAE)
- 95% CI: [53.0, 57.4]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 1.10 pts |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 55.1 | 1.1 pts |
| anchor | 55.4 | 2.7 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive last-known
anchor. ISM Services PMI is not published on FRED (proprietary) so no trend
sub-model in v1. Same architecture as ISM Manufacturing predictor.

Services is ~70% of US GDP so market reaction to ISM Services surprises is
typically larger than ISM Mfg. Sub-index breakout is what traders watch:
Business Activity, New Orders, Employment. Headline PMI is a composite.

Phase 2 target: add S&P Global Services PMI (released 3-5 days ahead) as
a leading sub-model. S&P Global publishes preliminary "flash" and final
readings; final correlates ~0.75 with ISM Services headline.
