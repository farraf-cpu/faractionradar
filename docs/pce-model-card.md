# PCE Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US PCE Price Index headline m/m (monthly, released ~30 days after ref month, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-pce.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to two sub-models. Same pattern
as PPI + CPI. Cron at 14:15 UTC daily (offset 15min from the 14:00/14:05/14:10
cluster of NFP/FOMC/PPI).

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field for "PCE Price Index m/m" or "Core PCE Price Index m/m" | ~0.05 |
| FRED PCEPI 6-mo trend | mean of last 6 published m/m %-changes of PCEPI (Personal Consumption Expenditures Chain-type Price Index) | ~0.10 |

Weights are `1 / MAE`. Consensus dominates in practice because it's the
tightest inflation-gauge consensus (analysts scrutinize PCE heavily as the
Fed's explicit target).

## Why consensus MAE is tighter than CPI/PPI

The Fed uses PCE as its 2% inflation target. Analysts publish PCE forecasts
with more model support than they do for headline CPI (which is more
retail-facing) or PPI (which is smaller institutional focus). Aggregated
consensus tends to be tighter — bootstrap ~0.05pp vs CPI's ~0.08pp.

## Phase 2 target

- Cleveland Fed nowcast for PCE (they publish separate CPI + PCE nowcasts)
- Core PCE decomposition — separate slug `pce-core-<date>` with its own
  sub-models (services ex-shelter is what the Fed watches most closely)
- CPI → PCE bridging model (headline CPI + core PCE typically move
  together with a small predictable lag; add a bridge sub-model that
  reads the most recent CPI print if the CPI release preceded PCE in the
  cycle, which it usually does by ~2 weeks)

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. Consensus + FRED trend,
  inverse-MAE. 5th event covered after NFP/CPI/PPI/FOMC.
