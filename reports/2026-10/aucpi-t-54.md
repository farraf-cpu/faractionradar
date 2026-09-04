# AU CPI prediction - target 2026-10-28 (T-54)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T17:41:40.865908+00:00

## Final pick

**+2.6%** y/y AU CPI

- Regime: upper end of RBA band
- 68% CI: [+2.46%, +2.74%]
- 95% CI: [+2.32%, +2.88%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.70% | 0.15pp |
| trend | +2.40% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
CPALTT01AUQ659N previous-quarter y/y anchor.

## Positioning

Second Phase 5 AUD predictor. AU CPI released quarterly by ABS ~4-5
weeks after quarter end at 11:30 AEDT. RBA target band is 2-3% CPI y/y.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 5 AUD expansion.
