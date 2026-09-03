# New Home Sales Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US New Home Sales (monthly, ~4th week, 10:00 ET, Census)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-newhome.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED HSN1F 3-month trend. Cron 15:20 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (K annualized) |
|-----------|--------|--------------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` | ~40 |
| FRED HSN1F 3-month trend | mean of last 3 New 1-Family Houses Sold values (SA annualized) | ~55 |

Value format: `650K`. Regime: hot (≥750K) / healthy (650-750K) / slowing (550-650K) / weak (<550K).

## Why more rate-sensitive than Existing

90%+ of new-home purchases are mortgage-financed. When 30-yr mortgage rates
move 50bp, new sales react faster than existing sales because builders
adjust pricing/incentives immediately while existing homeowners can wait
out rate cycles.

## Phase 2 targets

- **Mortgage rate 4-week lag** — Freddie Mac 30-yr fixed 4-week lag correlates ~-0.65
- **NAHB Housing Market Index cross** — HMI is a builder-sentiment survey released ~5 days ahead
- **Housing Starts as trailing anchor** — Starts leads Sales by 3-6 months on supply side

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 18th event covered.
