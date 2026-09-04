# JP CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** JP National Core CPI y/y (~19th-27th of following month, 08:30 JST / 23:30 UTC prior day)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-jpcpi.yml`

## What v1-simple-blend does

Consensus-only point estimate. Cron 18:20 UTC daily + 22:30 UTC on
release-day-eve.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` for "National Core CPI y/y" JPY | ~0.15 |

Soft-skips when consensus missing.

## Why consensus-only

FRED's Japan CPI series are all discontinued:
- `JPNCPIALLMINMEI` — last observation 2022-04-01, empty values
- `CPALTT01JPM659N` — last observation 2022-04-01, empty values
- `JPNCPICORMINMEI` — last observation 2022-04-01, empty values

Alternatives require e-Stat API integration (api.e-stat.go.jp, free
with registration, deferred to v1.1). This mirrors the German IFO
pattern where proprietary/dead-FRED source blocks a real trend anchor.

## Positioning

Second Phase 4 JPY predictor. National Core CPI (excluding fresh food)
is BOJ's preferred inflation gauge for policy signaling. Note the
Tokyo Core CPI leading indicator (~1 month early) is a separate
release; both may share this predictor via slug matching.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 4 JPY expansion.
  Consensus-only pending e-Stat API integration.
