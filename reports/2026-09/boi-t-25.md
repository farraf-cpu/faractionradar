# BOI Policy Rate prediction - target 2026-09-30 (T-25)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:51:59.615955+00:00

## Final pick

**3.75%** BOI Policy Rate

- 68% CI: [3.70%, 3.80%]
- 95% CI: [3.64%, 3.86%]
- Lean vs anchor: hold expected
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 3.75% | 0.05pp |
| anchor | 3.75% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01ILM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 18 (ILS expansion) rate-decision predictor. BOI meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 18 ILS expansion opens.
