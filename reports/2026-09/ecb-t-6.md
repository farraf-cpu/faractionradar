# ECB Rate prediction - target 2026-09-10 (T-6)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T10:45:18.838139+00:00

## Final pick

**2.25%** ECB Deposit Facility Rate

- 68% CI: [2.00%, 2.50%]
- 95% CI: [1.75%, 2.75%]
- Lean vs anchor: hold expected
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 2.25% | 0.25pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
ECBDFR current-rate anchor. Consensus MAE tight on rate-decision days
because analysts converge on likely move; anchor is no-change baseline.

## Positioning

First Phase 2 (EUR expansion) predictor. ECB Governing Council meets
~8x/year. Deposit Facility Rate is the primary ECB policy rate since
2022. Phase 2 target adds outcome distribution + eurodollar futures
implied rate similar to FOMC v2.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 2 EUR expansion opens.
