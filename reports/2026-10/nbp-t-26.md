# NBP Policy Rate prediction - target 2026-10-01 (T-26)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T22:18:51.990058+00:00

## Final pick

**5.25%** NBP Policy Rate

- 68% CI: [5.20%, 5.30%]
- 95% CI: [5.15%, 5.35%]
- Lean vs anchor: no anchor (dropped: scale mismatch)
- Sub-models used: consensus

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 5.25% | 0.05pp |
| anchor | - | 0.15pp |

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
