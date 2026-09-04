# Core CPI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Core CPI m/m (monthly, ~mid-month, 08:30 ET, BLS; same release as headline CPI)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-corecpi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:20 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.08 |
| FRED CPILFESL 6-mo mean m/m | Core CPI ex food + energy | ~0.15 |

Value format: `+0.3%` m/m.

## Positioning

Core CPI (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core CPI strips
those to show underlying inflation trend. Sticky-Fed indicator — prints
>0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

Phase 2 target adds Cleveland Fed nowcast + owner's-equivalent-rent
carve-out (shelter is the biggest sticky component; nowcasting shelter
sub-index would materially tighten MAE).

## Change log

- **v1-simple-blend** — first ship.
