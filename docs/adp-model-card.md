# ADP Non-Farm Employment Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US ADP Non-Farm Employment Change (monthly, Wed before NFP Fri, 08:15 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-adp.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED ADPMNUSNERSA 3-month trend.
Gate script computes next ADP Wednesday from the next NFP Friday (ADP is
released 2 days before NFP).

Sub-models:

| Sub-model | Source | Historical MAE (K jobs) |
|-----------|--------|--------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~30 |
| FRED ADPMNUSNERSA 3-month trend | mean of last 3 published ADP m/m change values (SA) | ~40 |

## Relationship to NFP

ADP correlates ~0.5-0.7 with NFP first-print. Post-2022 methodology change
(ADP now uses cell-phone geolocation + payroll data), correlation is
looser than pre-COVID. Directional signal only — not a NFP proxy.

Our NFP predictor's v1-bayesian-blend already ingests ADP as one input
sub-model. This standalone ADP predictor gives readers early visibility
into the ADP component 2 days before NFP fires.

## Phase 2 target

Post-ADP NFP-correlation-adjusted sub-model that translates the ADP
surprise into an expected NFP delta. Would replace / complement the
current NFP predictor's ADP input with a live-scored surprise term.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 12th event covered.
