# BOE Bank Rate prediction - target 2026-09-17 (T-13)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-09-04T17:03:48.206111+00:00

## Final pick

**3.73%** BoE Bank Rate

- 68% CI: [3.48%, 3.98%]
- 95% CI: [3.23%, 4.23%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 3.73% | 0.25pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IUDSOIA (SONIA) current-rate anchor. Point + sigma discretized over 25bp
buckets via normal CDF integration for outcome probabilities.

## Positioning

First Phase 3 (GBP expansion) rate-decision predictor. BoE MPC meets
~8x/year. Bank Rate is the primary policy instrument. Distribution
covers standard hike50/hike25/hold/cut25/cut50/cut75+ outcomes.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 3 GBP expansion opens.
