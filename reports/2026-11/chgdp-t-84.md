# AU GDP prediction - target 2026-11-27 (T-84)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:21:51.614845+00:00

## Final pick

**+0.6%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.28%, +0.88%]
- 95% CI: [-0.02%, +1.18%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +0.58% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CLVMNACSCAB1GQCH 4-qtr mean q/q trend.

## Positioning

Third Phase 8 CHF predictor. AU GDP q/q released quarterly by SECO
~9 weeks after quarter end at 09:00 CET.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 8 CHF expansion.
