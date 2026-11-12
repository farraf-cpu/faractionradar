# SARB Policy Rate prediction - target 2026-11-19 (T-7)

**Model version:** `v2-outcome-distribution`
**Published:** 2026-11-12T08:37:49.076260+00:00

## Final pick

**7.05%** SARB Policy Rate

- 68% CI: [6.90%, 7.20%] · sigma source: prior (inverse-MAE)
- 95% CI: [6.75%, 7.35%]
- Lean vs anchor: hold expected
- Sub-models used: anchor


## Outcome distribution (source: `unknown`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 0.6% |
| +25bp hike | 19.6% |
| hold | 59.5% **(modal)** |
| -25bp cut | 19.6% |
| -50bp cut | 0.6% |
| -75bp or deeper | 0.0% |


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.05pp |
| anchor | 7.05% | 0.15pp |

## Method

`v2-outcome-distribution`: inverse-MAE blend of FF consensus + FRED
IRSTCI01ZAM156N current-rate anchor. Point + sigma discretized over
25bp buckets via normal CDF for outcome probabilities.

## Positioning

First Phase 16 (ZAR expansion) rate-decision predictor. SARB meets
~8x/year. 25bp buckets match
FOMC/ECB/BOE/BOJ/RBA for UI consistency.

## Change log

- **v2-outcome-distribution (2026-11-12)** - first ship. Phase 16 ZAR expansion opens.
