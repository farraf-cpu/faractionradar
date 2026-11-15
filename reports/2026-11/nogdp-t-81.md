# AU GDP prediction - target 2026-11-24 (T-81)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T20:49:10.480117+00:00

## Final pick

**+0.5%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.20%, +0.80%]
- 95% CI: [-0.10%, +1.10%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +0.50% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CLVMNACSCAB1GQNO 4-qtr mean q/q trend.

## Positioning

Third Phase 11 NOK predictor. AU GDP q/q released quarterly by SSB
~9 weeks after quarter end at 09:00 CET.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 11 NOK expansion.
