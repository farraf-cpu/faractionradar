# ISM Manufacturing PMI Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US ISM Manufacturing PMI (monthly, 1st business day, 10:00 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-ism-mfg.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + naive last-known anchor. Sub-model
count is thinner than the CPI/PPI/PCE/Retail predictors because ISM PMI is
**not published on FRED** — the underlying diffusion index is proprietary
to Institute for Supply Management.

Sub-models:

| Sub-model | Source | Historical MAE (index points) |
|-----------|--------|-------------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~1.0 |
| Last-known anchor | live from calendar-worker `?read` → matched FF `previous` field (naive persistence) | ~2.5 |

Consensus dominates the blend (~2.5x tighter MAE). The anchor exists so we
never soft-skip when consensus is missing — but consensus is essentially
always present for ISM Mfg since it's a first-business-day marquee event.

## Value format

Diffusion index level (e.g. `48.5`, `50.2`), not a %-change. 50 = expansion/
contraction threshold. Regime annotation on report:
- ≥55: solid expansion
- 50-54: modest expansion
- 45-49: modest contraction
- <45: sharp contraction

## Why no FRED trend sub-model in v1

ISM restricts the PMI headline series. FRED historically had `NAPM` but the
release was frozen post-license-dispute (Institute for Supply Management
removed permission in the late 2010s). There is no clean FRED path to build
a 6-month trend or level series.

## Phase 2 target: regional Fed nowcasts

Empire State (NY Fed), Philly Fed, Dallas Fed, Kansas City Fed, and
Richmond Fed all publish current-activity diffusion indexes 5-10 days ahead
of ISM. Their weighted aggregate correlates ~0.85 with ISM Mfg.

Sub-models to add:
- Empire State general business conditions (FRED: `GACDISA066MSFRBNY` or peer)
- Philly Fed general activity (FRED: `PHIL_current`; series ID needs verification)
- Dallas Fed manufacturing business activity
- Kansas City Fed / Richmond Fed composite

Regional-nowcast composite should tighten MAE from ~1.0 to ~0.7 index points
based on FRB Cleveland's published correlation work.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. Consensus + anchor.
  7th event covered.
