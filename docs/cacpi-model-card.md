# CA CPI Predictor - Model Card

**Model version:** `v1.1-statcan`
**Event:** CA CPI y/y (monthly, ~3 weeks after reference month, 13:30 UTC, StatCan)
**Status:** Live via `predict-cacpi.yml`. **StatCan trend anchor auto-active — no key required.**

## What v1.1-statcan does

Inverse-MAE-weighted blend of 2 sub-models.

Sub-models:
| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" CAD | ~0.15 |
| StatCan WDS 3-mo trend | `www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods` vector v108785713 | ~0.20 |

Public no-auth API (Rule 39 exception, like brcpi SIDRA).

## Change log

- **v1.1-statcan (2026-09-05)** - swapped stale FRED CPALTT01CAM659N
  trend for live StatCan WDS API. Auto-active. Rule 39 fifth pattern
  (second public no-auth after SIDRA).
- **v1-simple-blend (2026-09-04)** - first ship. Phase 6 CAD expansion.

## Phase 6.1+ target

- CPI-trim / CPI-median / CPI-common (BOC's preferred core measures)
- Same StatCan WDS API, different vector IDs
