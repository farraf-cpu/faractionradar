# Riksbank Policy Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** Riksbank Policy Rate (~6x/year, 09:30 CET)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-riksbank.yml`

## What v2-outcome-distribution does

Same architecture as FOMC/ECB/BOE/BOJ/RBA/BOC/RBNZ/SNB v2: point
estimate + 25bp outcome distribution.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Policy Rate proxy | FRED `IR3TIB01SEM156N` (3-mo STIBOR) | ~0.30 |

## Method notes

- **Anchor caveat:** FRED `IRSTCI01SEM156N` (OECD Immediate <24h SE)
  is stale (last obs 2020-10, 6 years). Fell back to `IR3TIB01SEM156N`
  (3-month STIBOR) with inflated MAE 0.30pp per Rule 30.
- **Riksbank meets ~6x/year** with Monetary Policy Reports 4x. All
  2026-2027 dates hardcoded.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 9 SEK
  expansion opens.
