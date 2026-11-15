# SARB Policy Rate prediction - target 2026-09-17 (T-12)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T21:37:16.013118+00:00

## Final pick

**7.00%** SARB Policy Rate

- 68% CI: [6.85%, 7.15%]
- 95% CI: [6.70%, 7.30%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 7.00% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01ZAM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 16 (ZAR expansion) rate-decision predictor. SARB meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 16 ZAR expansion opens.
