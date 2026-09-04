# RIKSBANK Policy Rate prediction - target 2026-09-24 (T-20)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T20:26:12.954480+00:00

## Final pick

**1.78%** RIKSBANK Policy Rate

- 68% CI: [1.72%, 1.84%]
- 95% CI: [1.66%, 1.90%]
- Lean vs anchor: -17bp cut vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 1.75% | 0.05pp |
| anchor | 1.95% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IR3TIB01SEM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 9 (SEK expansion) rate-decision predictor. RIKSBANK meets
~~6x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 9 SEK expansion opens.
