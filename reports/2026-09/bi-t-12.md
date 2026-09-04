# BI Policy Rate prediction - target 2026-09-17 (T-12)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T23:20:42.543034+00:00

## Final pick

**5.88%** BI Policy Rate

- 68% CI: [5.73%, 6.03%]
- 95% CI: [5.58%, 6.18%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 5.88% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01IDM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 25 (IDR expansion) rate-decision predictor. BI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 25 IDR expansion opens.
