# AU GDP prediction - target 2026-11-27 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-24T04:06:06.741359+00:00

## Final pick

**+0.7%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.40%, +1.00%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.10%, +1.30%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.30 pp |
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
| trend | +0.70% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CLVMNACSCAB1GQSE 4-qtr mean q/q trend.

## Positioning

Third Phase 9 SEK predictor. AU GDP q/q released quarterly by SCB
~9 weeks after quarter end at 09:00 CET.

## Change log

- **v1-simple-blend (2026-11-24)** - first ship. Phase 9 SEK expansion.
