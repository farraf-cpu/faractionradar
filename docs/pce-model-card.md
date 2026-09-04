# PCE Predictor - Model Card

**Model version:** `v1.1-simple-blend`
**Event:** US PCE Price Index headline m/m (monthly, released ~30 days after ref month, 08:30 ET, BEA)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-pce.yml`

## What v1.1-simple-blend does

Inverse-MAE-weighted point estimate over up to 3 sub-models. Cron 14:15 UTC
daily + 10:30 UTC on release day.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` for "PCE Price Index m/m" | ~0.05 |
| **Cleveland Fed nowcast** | daily update from Cleveland Fed public JSON, 'PCE Inflation' series. Currently in PCE cycle (active for Sep 22 print). Soft-skips during CPI cycle. | **~0.04** (tightest) |
| FRED PCEPI 6-mo trend | mean of last 6 published m/m %-changes of PCEPI | ~0.10 |

Weights are `1 / MAE`. Cleveland Fed nowcast at 0.04pp is the tightest
sub-model when active. Consensus dominates when CF is in CPI cycle.

## Why consensus MAE is tighter than CPI/PPI

The Fed uses PCE as its 2% inflation target. Analysts publish PCE forecasts
with more model support than they do for headline CPI (which is more
retail-facing) or PPI (which is smaller institutional focus). Aggregated
consensus tends to be tighter - bootstrap ~0.05pp vs CPI's ~0.08pp.

## Cleveland Fed nowcast behavior

Cleveland Fed alternates their inflation nowcast between CPI cycle
(~T-14 through T-0 before CPI release) and PCE cycle (~T-14 through
T-0 before PCE release). During PCE cycle, our sub-model consumes
the latest non-empty value from their 'PCE Inflation' series. During
CPI cycle, our sub-model soft-skips and blend falls back to consensus
+ trend only.

## What v1.1 does NOT do (yet)

- **No Core PCE decomposition here** - Core PCE ships as separate slug
  (`corepce-<date>`, also v1.1 with same 3 sub-models applied to core series).
- **No CPI → PCE bridge** - headline CPI + core PCE typically move
  together with a small predictable lag. A bridge sub-model reading
  the most recent CPI print would tighten posterior.
- **Not true Bayesian** - inverse-MAE-as-variance-proxy weighting.

## Change log

- **v1.1-simple-blend (2026-09-04)** - added Cleveland Fed nowcast
  as 3rd sub-model (0.04pp MAE, tightest in blend).
- **v1-simple-blend (2026-09-03)** - first ship. Consensus + FRED trend.
