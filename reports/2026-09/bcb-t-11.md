# BCB Policy Rate prediction - target 2026-09-16 (T-11)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:27:47.620383+00:00

## Final pick

**21.00%** BCB Policy Rate

- 68% CI: [20.70%, 21.30%]
- 95% CI: [20.40%, 21.60%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 21.00% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
INTDSRBRM193N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 15 (BRL expansion) rate-decision predictor. BCB meets
~~12x/year (monthly Copom meeting). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 15 BRL expansion opens.
