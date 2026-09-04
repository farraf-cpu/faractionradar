# CPI Predictor — Model Card

**Model version:** `v1.2-simple-blend`
**Event:** US Consumer Price Index headline m/m (monthly, mid-month, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-cpi.yml`

## What v1.2-simple-blend does

Inverse-MAE-weighted point estimate over up to **five** sub-models. Runs from
the `predict-cpi.yml` workflow on daily crons; the gate script
(`scripts/should_run_cpi.py`) resolves the next CPI release date from the
calendar-worker's `/public/upcoming-marquee` endpoint and exits early on
non-cadence days.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.08 |
| **Cleveland Fed inflation nowcast** | daily update from Cleveland Fed public JSON (`nowcast_month.json`, 'CPI Inflation' series). Soft-skips during PCE cycle. | **~0.06** (tightest) |
| Kalshi prediction market | live from calendar-worker `/public/kalshi-implied` → `cpi.value_k` (interpolated ladder) | ~0.12 (bootstrap estimate) |
| FRED trimmed-mean CPI | `TRMMEANCPIM159SFRBDAL` (Dallas Fed 8% trimmed mean m/m); mean-reverting anchor that excludes top + bottom 8% tails | ~0.10 |
| FRED 6-mo trend | mean of last 6 published m/m %-changes of CPIAUCSL headline | ~0.15 |

Weights are `1 / MAE` per sub-model, normalized. The blended sigma is the
inverse-variance combination — reported as 68%/95% CIs in the payload.

If a sub-model is unavailable at run time (FF hasn't published forecast yet,
Kalshi ladder isn't interpolable, Cleveland Fed is in PCE cycle, FRED fetch
failed), it drops out. If all five are missing, the emitter soft-skips
(no error, no upload).

## Cleveland Fed nowcast behavior

Cleveland Fed publishes daily nowcasts alternating between CPI-window and
PCE-window depending on which is the next scheduled release. During the
CPI window (roughly T-14 through T-0 before CPI release), the 'CPI Inflation'
series in their `nowcast_month.json` has current values and our sub-model
consumes the latest non-empty value. During PCE window, the series returns
empty and our sub-model soft-skips.

This is the tightest sub-model in the blend when active (0.06pp MAE beats
FF consensus at 0.08pp).

## What v1.2 does NOT do (yet)

- **Not a full Bayesian model.** Weights are inverse-MAE priors from
  benchmarks, not empirical variance from resolutions. True Bayesian
  calibration blocked on live scoring accumulating.
- **Not a core-CPI model.** Headline m/m only. Core CPI ships as a separate
  slug (`corecpi-<date>`, v1.2 with 4 sub-models).
- **Not shelter-decomposed.** Shelter is ~1/3 of headline and drives most
  of recent post-COVID model error. Shelter carve-out sub-model is a
  future upgrade priority.

## Phase 3+ target

- **Shelter component tracker** — separately model the shelter sub-index
  (own release cycle + lag structure), reweight into headline. Cleveland
  Fed hints at owner's-equivalent-rent trajectory.
- **True Bayesian calibration** — replace inverse-MAE proxy with empirical
  posterior variance derived from resolutions.
- **Cross-sub-model correlation handling** — Kalshi tracks futures which
  track consensus surveys; treating them independently over-weights info.

## Change log

- **v1.2-simple-blend (2026-09-04)** — added Cleveland Fed inflation
  nowcast as 5th sub-model (0.06pp MAE, tightest in blend). Live during
  CPI cycle, soft-skips during PCE cycle.
- **v1.1-simple-blend (2026-09-03)** — added FRED trimmed-mean CPI (Dallas
  Fed 8% trim) as 4th sub-model.
- **v1-simple-blend (2026-09-03)** — three sub-model live blend (consensus
  + Kalshi + FRED trend, inverse-MAE weighted).
- **v1-beta (2026-09-01)** — placeholder shipped alongside NFP. Superseded.
