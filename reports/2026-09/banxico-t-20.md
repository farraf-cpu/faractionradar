# BANXICO Policy Rate prediction - target 2026-09-25 (T-20)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:04:16.987141+00:00

## Final pick

**7.00%** BANXICO Policy Rate

- 68% CI: [6.95%, 7.05%]
- 95% CI: [6.90%, 7.10%]
- Lean vs anchor: no anchor (dropped: scale mismatch)
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 7.00% | 0.05pp |
| anchor | - | 1.00pp |

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
