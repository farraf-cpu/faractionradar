# Core PCE Predictor — Model Card

**Model version:** `v1.1-simple-blend`
**Event:** US Core PCE m/m (monthly, ~last business day, 08:30 ET, BEA; same release as headline PCE)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-corepce.yml`

## What v1.1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:40 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.08 |
| Cleveland Fed nowcast | daily update from Fed Bank of Cleveland when CPI cycle active; soft-skip during PCE window | ~0.06 |
| FRED PCEPILFE 6-mo mean m/m | Core PCE ex food + energy | ~0.15 |

Cleveland Fed nowcast is the academic benchmark for near-term CPI accuracy; typically ~0.06pp MAE, tighter than FF consensus. Sub-model auto-activates when the CPI cycle is open (~T-14 before each CPI release) and returns None during the intervening PCE cycle.

Value format: `+0.3%` m/m.

## Positioning

Core PCE (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core PCE strips
those to show underlying inflation trend. Sticky-Fed indicator — prints
>0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

Phase 2 target adds Cleveland Fed nowcast + owner's-equivalent-rent
carve-out (shelter is the biggest sticky component; nowcasting shelter
sub-index would materially tighten MAE).

## Change log

- **v1-simple-blend** — first ship.
