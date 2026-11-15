# BOC Overnight Rate prediction - target 2026-09-10 (T-6)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T18:10:26.121622+00:00

## Final pick

**2.27%** BOC Overnight Rate

- 68% CI: [2.12%, 2.42%]
- 95% CI: [1.97%, 2.57%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 2.27% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01CAM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 6 (CAD expansion) rate-decision predictor. BOC meets
~8x/year on Wednesdays roughly every 6 weeks. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 6 CAD expansion opens.
