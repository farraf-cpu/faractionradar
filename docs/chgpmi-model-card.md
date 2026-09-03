# Chicago PMI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Chicago PMI (monthly, last business day, 09:45 ET, MNI Indicators)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-chgpmi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 15:40 UTC daily. Same architecture as
ISM Mfg/Svc — index is subscription-only (MNI Indicators), so no FRED trend.

Sub-models:

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~2.5 |
| Last-known anchor | live from calendar-worker `?read` → matched FF `previous` field | ~4.0 |

Value format: `52.5`. Regime: solid expansion (≥55) / modest expansion (50-55) / modest contraction (45-50) / sharp contraction (<45).

## Positioning

Regional (Midwest / Chicago) manufacturing gauge. Releases last business
day of month; ISM Manufacturing follows 1 business day later. Chicago
correlates ~0.75 with ISM Mfg — leading nowcast for ISM.

## Phase 2 targets

- **National ISM Mfg cross-check** — feed Chicago into `ismmfg` predictor as an extra sub-model
- **New Orders sub-index** — leads Chicago headline by 1-2 months

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 22nd event covered.
