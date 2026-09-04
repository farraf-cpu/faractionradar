# RBNZ Official Cash Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** RBNZ Official Cash Rate (~7x/year post-2022 reform, 02:00 UTC / 15:00 NZDT)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-rbnz.yml`

## What v2-outcome-distribution does

Same architecture as FOMC/ECB/BOE/BOJ/RBA/BOC v2: point estimate +
25bp outcome distribution.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current OCR proxy | FRED `IR3TIB01NZM156N` (3-mo Interbank NZ) | ~0.30 (inflated) |

## Method notes

- **Anchor caveat:** FRED `IRSTCI01NZM156N` (OECD Immediate <24h NZ)
  is stale (last obs 2024-12). Fell back to `IR3TIB01NZM156N`
  (3-month interbank rate), which typically carries ~15-25bp term
  premium above the OCR. MAE inflated to 0.30pp to reduce anchor
  weight in the blend. Consensus dominates when present (6x weight).
- **Post-2022 reform:** RBNZ moved from 8 to 7 meetings/year.
  All 2026-2027 meeting dates hardcoded in worker.

## What v2 does NOT do (yet)

- **No NZ OIS curve** — direct market-implied OCR path from NZ OIS
  would eliminate the term-premium issue.
- **Empirical variance calibration** blocked on resolutions.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 7 NZD
  expansion opens.
