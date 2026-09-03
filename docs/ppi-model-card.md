# PPI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Producer Price Index headline m/m (Final Demand, monthly, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-ppi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to two sub-models. Runs on the
same daily cron pattern as NFP/CPI/FOMC (14:10 UTC, offset 10min); gate
script `scripts/should_run_ppi.py` resolves the next PPI release date from
the calendar-worker's `/public/upcoming-marquee` endpoint.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.10 |
| FRED PPIFIS 6-mo trend | mean of last 6 published m/m %-changes of Producer Price Index by Industry: Final Demand | ~0.15 |

Weights are `1 / MAE`. Blended sigma is the inverse-variance combination.
If either sub-model is unavailable at run time, the other stands alone.
If both are missing, the emitter soft-skips.

## Why simpler than CPI

- **No prediction-market sub-model.** Kalshi doesn't have PPI event
  contracts (checked 2026-09-03) — PPI is less retail-visible than CPI.
  If Kalshi adds PPI markets later, wire in as a 3rd sub-model with
  bootstrap MAE ~0.12pp.
- **No trimmed-mean sub-model.** FRED doesn't publish a trimmed-mean PPI
  series analogous to Dallas Fed's `TRMMEANCPIM159SFRBDAL` for CPI.

## Phase 2 target: v2-sector-blend

Add a sector-decomposition sub-model:
- Energy Final Demand (`PPIFES`? confirm series ID)
- Food Final Demand
- Trade services carve-out (services PPI is where recent revisions concentrate)

PPI is more sector-heterogeneous than headline CPI — one strong sector move
(e.g. energy spike) can pull headline by 0.3pp+ without shifting the median
sector. Decomposition should tighten MAE ~30% based on FRB Cleveland's
public analysis.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. Consensus + FRED trend,
  inverse-MAE weighted. Same cadence pattern as NFP/CPI/FOMC.
