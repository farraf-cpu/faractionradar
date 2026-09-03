# CB Consumer Confidence Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US CB Consumer Confidence (monthly, last Tuesday, 10:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-confidence.yml`

## What v1-simple-blend does

Same architecture as ISM Mfg/Svc — index is proprietary (Conference Board),
so v1 relies on consensus + naive anchor. Cron 15:05 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (index pts) |
|-----------|--------|-----------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~2.0 |
| Last-known anchor | live from calendar-worker `?read` → matched FF `previous` field | ~4.0 |

Value format: index level `104.5`. Regime: elevated (≥120) / healthy (100-120) / cautious (85-100) / weak (<85).

## Phase 2 target

- **UMCSENT (UMich Consumer Sentiment)** — FRED-published free, correlates
  ~0.75 with CB Consumer Confidence; UMich preliminary releases mid-month,
  final end-of-month, both lead CB by 2-4 weeks
- **Sub-index decomposition** — Present Situation vs Expectations components
  diverge in inflection months
- **Weekly sentiment proxies** — Bloomberg Weekly Comfort, Redfin Homebuyer
  Demand composite as high-freq leading indicator

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 15th event covered.
