# JP Preliminary GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** JP Preliminary GDP q/q (~45 days after quarter end, 08:50 JST)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-jpgdp.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to 2 sub-models. Quarterly
cadence — 4 fires/year (matches JP quarterly GDP release cycle).

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` for "Prelim GDP q/q" JPY | ~0.15 |
| FRED NGDPRSAXDCJPQ 4-qtr trend | mean of last 4 published q/q %-changes (chained real GDP) | ~0.30 |

## Positioning

Third Phase 4 JPY predictor. Cabinet Office publishes Preliminary GDP
~45 days after quarter end at 08:50 JST. Final GDP follows ~2 months
later; this predictor targets the Preliminary release (larger market
impact).

## What v1 does NOT do (yet)

- **No consumption / capex / trade decomposition** — Preliminary GDP
  contribution breakdown is a standard analyst dashboard.
- **No BOJ Tankan cross-check** — Tankan (large mfr diffusion index)
  is a strong quarterly leading signal for GDP. Phase 4.1 could add
  a `boj-tankan` predictor + link the two.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 4 JPY expansion.
