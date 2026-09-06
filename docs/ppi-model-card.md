# PPI Predictor — Model Card

**Model version:** `v1.1-simple-blend`
**Event:** US Producer Price Index headline m/m (Final Demand, monthly, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-ppi.yml`

## What v1.1-simple-blend does

Inverse-MAE-weighted point estimate over up to three sub-models. Runs on the
same daily cron pattern as NFP/CPI/FOMC (14:10 UTC, offset 10min); gate
script `scripts/should_run_ppi.py` resolves the next PPI release date from
the calendar-worker's `/public/upcoming-marquee` endpoint.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.10 |
| FRED PPIFIS 6-mo trend | mean of last 6 published m/m %-changes of Producer Price Index by Industry: Final Demand | ~0.15 |
| FRED WPSFD4131 6-mo trend | mean of last 6 m/m %-changes of PPI Finished Goods less Foods and Energy (core-goods anchor) | ~0.15 |

Weights are `1 / MAE`. Blended sigma is the inverse-variance combination.
Any sub-model can be absent at run time — the others stand in. All three
missing = soft-skip.

## Core-goods anchor (v1.1)

Divergence between headline PPIFIS 6-mo trend and WPSFD4131 6-mo trend
signals the driver of near-term prints:
- **Headline > core-anchor:** food/energy pushing headline; likely
  transitory unless energy trend persists.
- **Headline ≈ core-anchor:** persistent underlying pressure; more
  Fed-relevant.
- **Headline < core-anchor:** food/energy dragging; core says pressure is
  still building beneath the surface.

## Why still no market sub-model

- Kalshi doesn't have PPI event contracts (checked 2026-09-03) — PPI is
  less retail-visible than CPI. If Kalshi adds PPI markets later, wire in
  as a 4th sub-model with bootstrap MAE ~0.12pp.
- No trimmed-mean PPI series on FRED analogous to Dallas Fed's
  `TRMMEANCPIM159SFRBDAL` for CPI.

## Phase 2 target

Finer sector decomposition when component data warrants:
- Energy Final Demand carve-out (`WPUFD42`)
- Food Final Demand carve-out (`WPUFD41`)
- Trade services carve-out (services PPI is where recent revisions
  concentrate)

## Change log

- **v1.1-simple-blend (2026-09-06)** — added FRED WPSFD4131 6-mo trend
  as core-goods anchor sub-model. Blend now up to 3 sub-models.
- **v1-simple-blend (2026-09-03)** — first ship. Consensus + FRED trend,
  inverse-MAE weighted. Same cadence pattern as NFP/CPI/FOMC.
