# Core PPI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Core PPI m/m (monthly, ~mid-month, 08:30 ET, BLS; same release as headline CPI)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-coreppi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:25 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.08 |
| FRED PPIFES 6-mo mean m/m | Core PPI ex food + energy | ~0.15 |

Value format: `+0.3%` m/m.

## Positioning

Core PPI (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core PPI strips
those to show underlying inflation trend. Sticky-Fed indicator — prints
>0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

Phase 2 target adds Cleveland Fed nowcast + owner's-equivalent-rent
carve-out (shelter is the biggest sticky component; nowcasting shelter
sub-index would materially tighten MAE).

## Change log

- **v1-simple-blend** — first ship.
