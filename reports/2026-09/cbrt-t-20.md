# CBRT Policy Rate prediction - target 2026-09-25 (T-20)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:40:38.153923+00:00

## Final pick

**38.11%** CBRT Policy Rate

- 68% CI: [38.05%, 38.17%]
- 95% CI: [37.99%, 38.23%]
- Lean vs anchor: -64bp cut vs current rate
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 38.00% | 0.05pp |
| anchor | 38.75% | 0.30pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
INTDSRTRM193N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 17 (TRY expansion) rate-decision predictor. CBRT meets
~~12x/year (monthly CBRT meeting). 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 17 TRY expansion opens.
