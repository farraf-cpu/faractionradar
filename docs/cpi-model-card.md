# CPI Predictor — Model Card

**Model version:** `v1.1-simple-blend`
**Event:** US Consumer Price Index headline m/m (monthly, mid-month, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-cpi.yml`

## What v1.1-simple-blend does

Inverse-MAE-weighted point estimate over up to four sub-models. Runs from
the `predict-cpi.yml` workflow on the same daily cron as NFP; the gate script
(`scripts/should_run_cpi.py`) resolves the next CPI release date from the
calendar-worker's `/public/upcoming-marquee` endpoint and exits early on
non-cadence days.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.08 |
| Kalshi prediction market | live from calendar-worker `/public/kalshi-implied` → `cpi.value_k` (interpolated ladder) | ~0.12 (bootstrap estimate) |
| FRED trimmed-mean CPI | `TRMMEANCPIM159SFRBDAL` (Dallas Fed 8% trimmed mean m/m); mean-reverting anchor that excludes top + bottom 8% tails | ~0.10 |
| FRED 6-mo trend | mean of last 6 published m/m %-changes of CPIAUCSL headline | ~0.15 |

Weights are `1 / MAE` per sub-model, normalized. The blended sigma is the
inverse-variance combination — reported as 68%/95% CIs in the payload.

If a sub-model is unavailable at run time (FF hasn't published forecast yet,
Kalshi ladder isn't interpolable, FRED fetch failed), it drops out. If all
four are missing, the emitter soft-skips (no error, no upload).

## What v1-simple-blend is NOT

- **Not a trained model.** No ML component; weights are hardcoded from
  published/estimated MAE benchmarks rather than fit on data.
- **Not a core-CPI model.** Headline m/m only. Core CPI ships in Phase 2
  as a separate slug (`cpi-core-YYYY-MM-DD`).
- **Not shelter-decomposed.** Shelter is ~1/3 of headline CPI and drives most
  of the recent post-COVID model error; a shelter carve-out sub-model is a
  Phase 2 upgrade priority.

## Phase 2 target: v2-bayesian-blend

Add three sub-models to bring CPI parity with the NFP predictor:

- **Cleveland Fed inflation nowcast** — public, daily-updated during the
  release cycle, historical MAE ~0.06pp on headline
- **Trimmed-mean CPI** — 8% trimmed mean series (published by FRB Dallas)
  as a mean-reverting anchor
- **Shelter component tracker** — separately model the shelter sub-index
  (has its own release cycle + lag structure) and reweight into headline

Same Bayesian inverse-variance blend architecture as NFP. Target MAE < 0.10pp
on headline m/m over ~40 post-COVID months.

## Change log

- **v1.1-simple-blend (2026-09-03)** — added FRED trimmed-mean CPI (Dallas
  Fed 8% trim, `TRMMEANCPIM159SFRBDAL`) as a 4th sub-model. Same inverse-MAE
  weighting; extra sub-model tightens blended sigma from ~0.07pp to ~0.05pp
  when all four sub-models are available. First fire: T-4 or later for Sep 11.
- **v1-simple-blend (2026-09-03)** — three sub-model live blend. Consensus +
  Kalshi implied + FRED trend, inverse-MAE weighted. Superseded within hours
  by v1.1 (trimmed-mean addition).
- **v1-beta (2026-09-01)** — placeholder shipped alongside NFP. Superseded.
