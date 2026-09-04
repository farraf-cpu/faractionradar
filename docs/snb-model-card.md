# SNB Policy Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** SNB Policy Rate (~4x/year, 09:30 CET / 08:30 UTC winter)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-snb.yml`

## What v2-outcome-distribution does

Same architecture as FOMC/ECB/BOE/BOJ/RBA/BOC/RBNZ v2: point estimate
+ 25bp outcome distribution.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Policy Rate proxy | FRED `IR3TIB01CHM156N` (3-mo CHF rate, SARON-adjacent) | ~0.30 |

## Method notes

- **Anchor caveat:** FRED `IRSTCI01CHM156N` (OECD Immediate <24h CH)
  is stale (last obs 2024-03). Fell back to `IR3TIB01CHM156N`
  (3-month CHF rate, closely tracks SARON). MAE inflated to 0.30pp
  as with RBNZ (Rule 30). Consensus dominates when present.
- **Quarterly cadence:** SNB reviews policy quarterly at Monetary
  Policy Assessments. Only 4 meetings/year.
- **Low-rate regime:** SNB moves in 25-50bp increments; historically
  used SARON reference rate targeting since 2019.

## What v2 does NOT do (yet)

- **No SARON futures curve** — direct SARON forward strip would
  eliminate term-premium anchor bias.
- **Empirical variance calibration** blocked on resolutions.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 8 CHF
  expansion opens.
