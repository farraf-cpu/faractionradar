# BANXICO Policy Rate prediction - target 2026-09-25 (T-20)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:09:21.607511+00:00

## Final pick

**5.19%** BANXICO Policy Rate

- 68% CI: [4.19%, 6.19%]
- 95% CI: [3.19%, 7.19%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 5.19% | 1.00pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01MXM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 13 (MXN expansion) rate-decision predictor. BANXICO meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 13 MXN expansion opens.
