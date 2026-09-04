# AU GDP prediction - target 2026-11-27 (T-84)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:26:15.291555+00:00

## Final pick

**+0.4%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.29%, +0.57%]
- 95% CI: [+0.14%, +0.71%]
- Lean vs consensus: above consensus by 0.13pp
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.30% | 0.15pp |
| trend | +0.68% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CLVMNACSCAB1GQSE 4-qtr mean q/q trend.

## Positioning

Third Phase 9 SEK predictor. AU GDP q/q released quarterly by SCB
~9 weeks after quarter end at 09:00 CET.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 9 SEK expansion.
