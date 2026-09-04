# NORGES Policy Rate prediction - target 2026-09-18 (T-14)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T20:49:03.450925+00:00

## Final pick

**4.25%** NORGES Policy Rate

- 68% CI: [4.10%, 4.40%]
- 95% CI: [3.95%, 4.55%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 4.25% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01NOM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 11 (NOK expansion) rate-decision predictor. NORGES meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 11 NOK expansion opens.
