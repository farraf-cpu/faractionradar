# Core CPI Predictor - Model Card

**Model version:** `v1.2-simple-blend`
**Event:** US Core CPI m/m (monthly, ~mid-month, 08:30 ET, BLS; same release as headline CPI)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-corecpi.yml`

## What v1.2-simple-blend does

Inverse-MAE-weighted blend of 4 sub-models. Cron 17:20 UTC daily +
10:30 UTC on release day.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.08 |
| **Cleveland Fed nowcast** | daily update, 'Core CPI Inflation' series; soft-skips during PCE cycle | **~0.06** (tightest) |
| FRED Dallas trimmed-mean | `TRMMEANCPIM159SFRBDAL` 8% trimmed mean m/m | ~0.10 |
| FRED CPILFESL 6-mo mean m/m | Core CPI ex food + energy | ~0.15 |

Value format: `+0.3%` m/m.

## Positioning

Core CPI (ex food + energy) is the Fed's actual inflation focus.
Headline CPI is noisier from oil/food volatility; Core CPI strips
those to show underlying inflation trend. Sticky-Fed indicator - prints
>0.3% m/m sustain hawkish pressure; <0.2% opens easing path.

Same 4 sub-models as headline CPI predictor, applied to Core CPI series
(CPILFESL for FRED trend, 'Core CPI Inflation' for Cleveland Fed).

## What v1.2 does NOT do (yet)

- **No shelter carve-out** — shelter is ~40% of Core CPI. Separate
  sub-model would materially tighten posterior.
- **No trimmed-mean CORE** — Dallas Fed 8% trimmed-mean is HEADLINE
  based. A trimmed-mean core would be a legitimate additional signal.
- **Not true Bayesian** — same inverse-MAE-as-variance-proxy weighting
  as headline CPI predictor.

## Change log

- **v1.2-simple-blend (2026-09-04)** — added Dallas Fed trimmed-mean
  as 4th sub-model.
- **v1.1-simple-blend (2026-09-04)** — added Cleveland Fed nowcast.
- **v1-simple-blend (2026-09-04)** — first ship, 2 sub-models
  (consensus + FRED trend).
