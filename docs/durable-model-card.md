# Durable Goods Orders Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Durable Goods Orders m/m headline (monthly, ~24th-28th, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-durable.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED DGORDER 3-month trend. Cron
at 14:55 UTC daily.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.5 |
| FRED DGORDER 3-month trend | mean of last 3 m/m %-changes of Durable Goods Orders (SA level) | ~0.8 |

## Why bands are wide

Durables is one of the noisiest monthly prints. A single Boeing 737 MAX
order can swing headline by 2pp+. Consensus MAE (~0.5pp) reflects this;
blend MAE inherits the wider band.

Traders watch Core Durable Goods (ex-transportation) more than headline
for the same reason.

## Phase 2 targets

- **Core Durable Goods split** — separate slug `durable-core-<date>` for
  the ex-transportation version. Markets react more to Core because it
  strips the Boeing/defense noise
- **Boeing 737 MAX orders tracker** — Boeing reports monthly commercial
  aircraft orders separately; subtract from headline to build a
  "durable ex-Boeing" leading indicator
- **Capital goods orders sub-index** — Non-defense capital goods orders
  ex-aircraft are the standard capex proxy in GDP nowcasting; add as a
  separate slug in Phase 2

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 13th event covered.
