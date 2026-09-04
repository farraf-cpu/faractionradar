# IN CPI Predictor - Model Card

**Model version:** `v1.1-mospi`
**Event:** IN CPI y/y (monthly, ~12th of following month, 17:30 IST, MoSPI)
**Status:** Live via `predict-incpi.yml`

## What v1.1-mospi does

Inverse-MAE-weighted point estimate over up to 2 sub-models.

Sub-models:
| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" INR | ~0.15 |
| MoSPI 3-mo mean trend | data.gov.in API (default resource UUID configurable via env) | ~0.25 |

**Consensus-only fallback:** if `MOSPI_APP_ID` env unset or API errors,
predictor falls back to consensus-only (v1 behavior).

## Activation

1. Register at **https://data.gov.in/user/register** (free, ~5 min).
2. Add resulting API key as GHA secret `MOSPI_APP_ID`.
3. (Optional) If default resource UUID stops working, override with
   `MOSPI_RESOURCE_ID` secret pointing to current "All India Consumer
   Price Index Numbers" dataset UUID on data.gov.in.
4. Next scheduled cron picks up MoSPI trend automatically.

## Why MoSPI is required

- FRED `CPALTT01INM659N` stale (last obs 2025-03).
- data.gov.in is India's Open Government Data portal and the only free
  fresh source of monthly MoSPI CPI data.
- MoSPI publishes All India CPI Combined y/y ~12th of following month;
  data.gov.in typically updates within 24 hours.

Follows Rule 39 pattern (native CB API integration) established by
jpcpi v1.1-estat (Phase 27) and krcpi v1.1-kosis (Phase 28).

## Change log

- **v1.1-mospi (2026-09-05)** - added MoSPI trend anchor sub-model
  via data.gov.in (opt-in via MOSPI_APP_ID).
- **v1-simple-blend (2026-09-04)** - first ship. Phase 14 INR.
