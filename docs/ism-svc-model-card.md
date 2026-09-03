# ISM Services PMI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US ISM Services PMI (monthly, ~3rd business day, 10:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-ism-svc.yml`

## What v1-simple-blend does

Mirror of `emit_ism_mfg.py`. Inverse-MAE-weighted blend of consensus + naive
last-known-value anchor. Cron at 14:30 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (index points) |
|-----------|--------|-------------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~1.1 |
| Last-known anchor | live from calendar-worker `?read` → matched FF `previous` field (naive persistence) | ~2.7 |

## Why bigger market mover than ISM Mfg

Services are ~70% of US GDP. Surprise moves in ISM Services headline
typically move UST yields and USD more than an equivalent-magnitude
manufacturing surprise. Sub-index breakout also matters:
- **Business Activity** — closest proxy to "GDP now"
- **New Orders** — leading indicator
- **Employment** — leads NFP by ~2 weeks
- **Prices Paid** — proxy for service-sector inflation pressure

## Why no FRED sub-model in v1

Same as ISM Mfg: series is proprietary to Institute for Supply Management.
No clean FRED path.

## Phase 2 target

Add **S&P Global Services PMI** as a leading sub-model. S&P Global publishes
preliminary "flash" 5-7 days ahead of ISM Services and a final reading 3-5
days ahead. Final S&P Global correlates ~0.75 with ISM Services headline.

If S&P Global has a public API or FRED redistributes it, wire in as a 3rd
sub-model with expected MAE ~0.8 index points — would tighten our headline
blend to sub-1.0 MAE.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 8th event covered.
