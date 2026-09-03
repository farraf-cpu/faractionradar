# Retail Sales Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Advance Retail Sales headline m/m (monthly, mid-month, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-retail.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of up to 2 sub-models. Same pattern as PPI + PCE.
Daily cron at 14:20 UTC (offset from NFP/CPI 14:00, FOMC 14:05, PPI 14:10,
PCE 14:15).

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` for "Retail Sales m/m" | ~0.30 |
| FRED RSXFS 6-mo trend | mean of last 6 published m/m %-changes of Advance Retail Sales: Retail Trade and Food Services (SA) | ~0.40 |

## Why MAE is wider than inflation prints

Retail sales is one of the noisier monthly prints. Consumer spending swings
sharply on:
- Weather (severe cold/heat compresses foot traffic)
- Holiday timing (Easter/Thanksgiving falling in different months)
- One-off sector moves (auto recalls, gas price shocks, back-to-school shifts)

Consensus MAE ~0.30pp reflects this — analysts model it less tightly than
they do PCE or CPI. Blend MAE inherits the wider band.

Also: `lean_vs_consensus` uses 0.05pp threshold for "in line" (vs 0.02pp for
inflation prints) — anything within 5bp of consensus on retail sales is
noise-level agreement.

## Phase 2 targets

- **Auto-sales adjustment sub-model** — Ward's Intelligence publishes monthly
  auto SAAR ~5-7 days ahead of Census release. Autos are ~20% of headline
  retail sales, so an early auto SAAR read tightens headline forecast
  materially.
- **Gas station sales carve-out** — headline retail includes gas station
  sales; large oil-price swings distort m/m. Carve-out sub-model would use
  EIA weekly gas price change as a proxy input.
- **Core Retail Sales split** — separate slug `retail-core-<date>` for the
  ex-autos version (which is what markets watch on shopping-driven months).

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 6th event covered after
  NFP/CPI/PPI/PCE/FOMC.
