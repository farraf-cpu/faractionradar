# BOK Policy Rate prediction - target 2026-10-16 (T-42)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T20:58:33.695046+00:00

## Final pick

**2.54%** BOK Policy Rate

- 68% CI: [2.39%, 2.69%]
- 95% CI: [2.24%, 2.84%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 2.54% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01KRM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 12 (KRW expansion) rate-decision predictor. BOK meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 12 KRW expansion opens.
