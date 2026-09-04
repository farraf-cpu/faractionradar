# RBNZ Official Cash Rate prediction - target 2026-10-08 (T-34)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T20:10:27.722938+00:00

## Final pick

**2.68%** RBNZ Official Cash Rate

- 68% CI: [2.38%, 2.98%]
- 95% CI: [2.08%, 3.28%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 2.68% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IR3TIB01NZM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 7 (NZD expansion) rate-decision predictor. RBNZ meets
~7x/year (post-2022 reform). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 7 NZD expansion opens.
