# Empire State Manufacturing Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Empire State Manufacturing Index (monthly, ~15th, 08:30 ET, NY Fed)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-empire.yml`

## What v1-simple-blend does

Inverse-MAE blend. Cron 15:45 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~4 |
| FRED GACDISA066MSFRBNY 3-month trend | mean of last 3 Empire State General Business Conditions values (SA) | ~5 |

Value format: signed 1-decimal, e.g. `-5.3` or `+8.7`. **Zero = neutral** (unlike ISM/Chicago at 50). Regime: solid regional expansion (≥10) / modest expansion (0-10) / modest contraction (-10 to 0) / sharp contraction (<-10).

## Positioning

First regional Fed survey each month — earliest signal in the manufacturing
survey chain. Composite of 5 regional Feds (Empire + Philly + Dallas + KC +
Richmond) correlates ~0.85 with ISM Mfg headline.

## Phase 2 targets

- **New Orders sub-index** — leads by 1-2 months
- **Feed into ismmfg predictor** — alongside Chicago PMI as leading sub-model

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 23rd event covered.
