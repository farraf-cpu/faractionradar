# Existing Home Sales Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Existing Home Sales (monthly, ~20th-24th, 10:00 ET, NAR)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-existing.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED EXHOSLUSM495S 3-month trend.
Cron 15:15 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE |
|-----------|--------|----------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~50K annualized |
| FRED EXHOSLUSM495S 3-month trend | mean of last 3 Existing Home Sales values (SA annualized, converted K→M) | ~80K annualized |

Value format: `4.05M` (millions annualized). Regime: hot resale (≥5.5M) /
healthy (4.5-5.5M) / slow (3.8-4.5M) / frozen (<3.8M).

## Phase 2 targets

- **Mortgage rate lag** — Freddie Mac 30-yr fixed 8-week lag correlates ~-0.6
- **Pending Home Sales cross** — NAR Pending leads Existing by 1-2 months
- **Regional decomposition** — South is ~45% of national

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 17th event covered.
