# UMich Consumer Sentiment (Preliminary) Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US UMich Consumer Sentiment Preliminary (monthly, ~mid-month Friday, 10:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-umich.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 15:25 UTC daily. Preliminary print only —
Revised (end-of-month) is Phase 2.

Sub-models:

| Sub-model | Source | Historical MAE (index pts) |
|-----------|--------|-----------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~1.5 |
| FRED UMCSENT 3-month trend | mean of last 3 UMich Sentiment values | ~2.5 |

Value format: `72.5` (1 decimal, index level). Regime: strong (≥90) /
moderate (75-90) / weak (60-75) / recession-level (<60).

## Why simpler than CB Confidence

UMCSENT is on FRED — we get real trend data. CB Consumer Confidence is
proprietary, so its predictor uses consensus + naive anchor only.

## Relationship to CB Consumer Confidence

Correlates ~0.75 with CB Confidence but releases 2-3 weeks earlier
(preliminary comes mid-month vs CB's last Tuesday). Leading indicator for
CB Confidence direction changes.

## Phase 2 targets

- **Inflation Expectations sub-index split** — UMich publishes 1-year +
  5-year inflation expectations; Fed watches these; separate slugs
- **Revised (Final) split** — end-of-month release with sample doubled;
  add `umich-revised-<date>` slug
- **Weekly Bloomberg Consumer Comfort cross** as high-frequency leading

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 19th event covered.
