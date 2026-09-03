# JOLTS Job Openings Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US JOLTS Job Openings (monthly, ~1st week, 10:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-jolts.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron at 15:00 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (openings) |
|-----------|--------|----------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~150K |
| FRED JTSJOL 3-month trend | mean of last 3 JOLTS Job Openings levels (SA, converted from K to M) | ~250K |

## Value format

Millions of openings, 2 decimals + `M` suffix: `7.20M`. Regime annotation:
- ≥9.0M: extremely tight labor demand
- 8.0-9.0M: tight
- 7.0-8.0M: moderating
- <7.0M: softening

## Why this matters

Openings/Unemployed ratio is Fed Chair Powell's preferred labor-tightness
gauge. Ratio >1.5 = extremely tight; ~1.0 = balanced; <0.8 = slack. Since
the ratio requires U-3 unemployment level, our regime labels use the
openings level directly.

## Phase 2 targets

- **Openings/Unemployed ratio** — cross-fetch NFP unemployment from KV,
  publish ratio alongside headline as Fed-relevant metric
- **Quits Rate sub-model** — JTSQUL leads Openings by ~1 month
- **Hires vs Separations gap** — JTSHIL − JTSTSL sanity checks Openings trend

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 14th event covered.
