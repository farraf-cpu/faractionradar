# AU GDP prediction - target 2026-11-24 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-24T06:15:49.727414+00:00

## Final pick

**+0.4%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.10%, +0.70%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.20%, +1.00%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +0.40% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CLVMNACSCAB1GQNO 4-qtr mean q/q trend.

## Positioning

Third Phase 11 NOK predictor. AU GDP q/q released quarterly by SSB
~9 weeks after quarter end at 09:00 CET.

## Change log

- **v1-simple-blend (2026-11-24)** - first ship. Phase 11 NOK expansion.
