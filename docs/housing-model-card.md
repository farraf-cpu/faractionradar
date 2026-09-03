# Housing Starts Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Housing Starts (monthly, ~16th-19th, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-housing.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED HOUST 3-month trend. Cron
at 14:40 UTC daily (offset from earlier events in the cascade).

Sub-models:

| Sub-model | Source | Historical MAE (thousands of starts) |
|-----------|--------|--------------------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field (format `1.36M`) | ~40 |
| FRED HOUST 3-month trend | mean of last 3 published HOUST values (SA, converted from thousands to millions) | ~60 |

## Value format

Millions of annualized starts, 2 decimals + `M` suffix: `1.35M`. FRED HOUST
reports as thousands (`1350`) so trend divides by 1000 to match.

## Regime annotation

Report tags cycle-level context:
- ≥1.6M: strong construction cycle
- 1.4-1.6M: moderate
- 1.2-1.4M: slowing
- <1.2M: weak

## Why 3-month trend (not 6-month)

Housing is more trend-persistent than employment or inflation, but it also
turns sharply on mortgage-rate inflections. A 6-month window smooths past
those turns and lags. 3-month captures direction changes with acceptable
noise.

## Phase 2 targets

- **Building Permits as co-anchor** — FRED PERMIT publishes same day as
  Starts; Permits lead Starts by 1-2 months. Use as an independent
  anchor sub-model rather than as trend input alone.
- **Mortgage rate cross** — Freddie Mac 30-year fixed (FRED MORTGAGE30US)
  is the primary Starts driver. Add a mortgage-rate-change sub-model that
  flags direction when the 4-week average moves >25bp.
- **Regional decomposition** — Northeast/Midwest/South/West follow
  different seasonal patterns; South is ~50% of national.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 10th event covered.
