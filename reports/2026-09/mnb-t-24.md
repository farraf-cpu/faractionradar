# MNB Policy Rate prediction - target 2026-09-29 (T-24)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T22:09:28.912284+00:00

## Final pick

**6.40%** MNB Policy Rate

- 68% CI: [6.35%, 6.45%]
- 95% CI: [6.30%, 6.51%]
- Lean vs anchor: +30bp move vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 6.50% | 0.05pp |
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
