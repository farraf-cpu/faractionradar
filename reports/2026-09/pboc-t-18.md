# PBOC Policy Rate prediction - target 2026-09-22 (T-18)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T20:36:07.834248+00:00

## Final pick

**3.07%** PBOC Policy Rate

- 68% CI: [3.01%, 3.13%]
- 95% CI: [2.95%, 3.19%]
- Lean vs anchor: +17bp move vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 3.10% | 0.05pp |
| anchor | 2.90% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
INTDSRCNM193N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 10 (CNY expansion) rate-decision predictor. PBOC meets
~~12x/year (monthly LPR fixing). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 10 CNY expansion opens.
