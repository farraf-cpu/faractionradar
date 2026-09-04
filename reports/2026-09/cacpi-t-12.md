# CA CPI prediction - target 2026-09-16 (T-12)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T18:04:45.245266+00:00

## Final pick

**+2.3%** y/y CA CPI

- Regime: upper end of BOC band
- 68% CI: [+2.15%, +2.44%]
- 95% CI: [+2.01%, +2.58%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.30% | 0.15pp |
| trend | +2.29% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CPALTT01CAM659N 3-mo mean y/y anchor.

## Positioning

Second Phase 6 CAD predictor. CA CPI released quarterly by StatCan ~4-5
weeks after quarter end at 08:30 EST. BOC target 2% CPI y/y (1-3% band) CPI y/y.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 6 CAD expansion.
