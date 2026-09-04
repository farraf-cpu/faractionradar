# BOJ Policy Rate prediction - target 2026-09-19 (T-15)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T17:26:15.254179+00:00

## Final pick

**0.77%** BOJ Policy Rate

- 68% CI: [0.72%, 0.83%]
- 95% CI: [0.67%, 0.88%]
- Lean vs anchor: -7bp cut vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 0.75% | 0.05pp |
| anchor | 0.84% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01JPM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF integration for outcome probabilities.

## Positioning

First Phase 4 (JPY expansion) rate-decision predictor. BOJ MPC meets
~8x/year. Post-2024 exit from NIRP, BOJ moves in 15-25bp steps.
25bp buckets match FOMC/ECB/BOE for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 4 JPY expansion opens.
