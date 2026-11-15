# AU GDP prediction - target 2026-12-03 (T-90)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T17:54:28.142439+00:00

## Final pick

**+0.6%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.32%, +0.92%]
- 95% CI: [+0.02%, +1.22%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +0.62% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
NGDPRSAXDCAUQ 4-qtr mean q/q trend.

## Positioning

Third Phase 5 AUD predictor. AU GDP q/q released quarterly by ABS
~9 weeks after quarter end at 11:30 AEDT.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 5 AUD expansion.
