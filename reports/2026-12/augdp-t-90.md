# AU GDP prediction - target 2026-12-03 (T-90)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T17:41:42.075423+00:00

## Final pick

**+0.5%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.40%, +0.68%]
- 95% CI: [+0.26%, +0.82%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.50% | 0.15pp |
| trend | +0.62% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
NGDPRSAXDCAUQ 4-qtr mean q/q trend.

## Positioning

Third Phase 5 AUD predictor. AU GDP q/q released quarterly by ABS
~9 weeks after quarter end at 11:30 AEDT.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 5 AUD expansion.
