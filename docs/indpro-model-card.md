# Industrial Production Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Industrial Production m/m (monthly, ~15th-17th, 09:15 ET, Federal Reserve)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-indpro.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 15:35 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.3 |
| FRED INDPRO 3-month trend | mean of last 3 m/m %-changes of Industrial Production Index | ~0.4 |

Value format: `+0.3%` m/m.

## Why this matters

Direct physical-output measure — manufacturing + mining + utilities.
More concrete than PMI (which is a survey). Sensitive to:
- Weather (utilities component swings with heating/cooling demand)
- Auto plant cycles (Mfg component; single plant shutdown = 0.3pp)
- Oil prices (mining component)

## Phase 2 targets

- **Capacity Utilization companion** — TCU releases same day, add `capacity-<date>` slug
- **Manufacturing-only sub-index** — IPMANSICS strips utilities weather noise
- **Auto production tracker** — Ward's Intelligence has weekly plant data

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 21st event covered.
