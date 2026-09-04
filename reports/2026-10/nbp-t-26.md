# NBP Policy Rate prediction - target 2026-10-01 (T-26)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T22:23:42.001550+00:00

## Final pick

**3.74%** NBP Policy Rate

- 68% CI: [3.59%, 3.89%]
- 95% CI: [3.44%, 4.04%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 3.74% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01PLM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 21 (PLN expansion) rate-decision predictor. NBP meets
~12x/year (monthly). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 21 PLN expansion opens.
