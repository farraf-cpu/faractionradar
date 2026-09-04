# MNB Policy Rate prediction - target 2026-09-29 (T-24)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T22:14:50.662303+00:00

## Final pick

**6.11%** MNB Policy Rate

- 68% CI: [5.96%, 6.26%]
- 95% CI: [5.81%, 6.41%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 6.11% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01HUM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 20 (HUF expansion) rate-decision predictor. MNB meets
~12x/year (monthly). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 20 HUF expansion opens.
