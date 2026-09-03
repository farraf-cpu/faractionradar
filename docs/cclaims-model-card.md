# Continuing Claims Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Continuing Jobless Claims (weekly, Thursday 08:30 ET)
**Status:** Live — cadence T-2 + T-1 via `predict-cclaims.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 15:30 UTC daily. Weekly cadence like
Initial Claims — T-2 (Tue) + T-1 (Wed) only.

Sub-models:

| Sub-model | Source | Historical MAE (K claims) |
|-----------|--------|----------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~20 |
| FRED CCSA 4-week trend | mean of last 4 Continued Claims values (SA, K → M) | ~30 |

Value format: `1.78M`. Regime: elevated persistence (≥1.9M) / typical
(1.7-1.9M) / moderate (1.5-1.7M) / tight (<1.5M).

## Relationship to Initial Claims

Continuing = pool of people still on benefits after initial filing.
Rising Continuing alongside flat Initial usually means hiring has slowed
(people can't find new jobs after being laid off). Directional cross-check
for Initial Claims interpretation.

## Phase 2 targets

- **Initial/Continuing ratio** — Continuing / Initial; ratio rising = hiring softening
- **Insured Unemployment Rate** — direct labor-slack metric

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 20th event covered.
