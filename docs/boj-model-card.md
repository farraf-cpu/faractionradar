# BOJ Policy Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** BOJ Policy Rate (MPC decision, ~8x/year, 03:00 UTC / 12:00 JST)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-boj.yml`

## What v2-outcome-distribution does

Same architecture as FOMC/ECB/BOE v2: point estimate + probability
distribution over standard 25bp buckets. Post-2024 exit from NIRP,
BOJ has been moving in 15-25bp increments.

Output shape (`ourCall.outcomeDistribution`):
```json
{
  "hike50":     0.02,
  "hike25":     0.20,
  "hold":       0.70,
  "cut25":      0.07,
  "cut50":      0.01,
  "cut75_plus": 0.00,
  "modal":      "hold"
}
```

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Policy Rate anchor | FRED `IRSTCI01JPM156N` (OECD Immediate Rates <24h JP) | ~0.15 |

## Method notes

- **IRSTCI01JPM156N tracks BOJ Policy Rate** within ~5-10bp, updates
  monthly. It is the OECD's Immediate Rates <24h series for Japan.
  FRED `INTDSRJPM193N` (Japan Discount Rate) is discontinued since 2017
  and unusable, same failure mode as UK's `INTDSRGBM193N` in Phase 3.
- **Language barrier scope:** BOJ publishes primary policy statements
  in Japanese. This predictor consumes FF's translated forecast field
  (same source as USD/EUR/GBP predictors); model card copy is in
  English. No BOJ document parsing required.

## What v2 does NOT do (yet)

- **No JGB futures curve** — 10Y JGB yield implied policy expectations
  would add a strong forward-looking signal.
- **No Kalshi / prediction market ladder** for BOJ (Kalshi doesn't
  currently list BOJ meeting outcomes).
- **Empirical variance calibration** blocked on resolutions.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 4 JPY
  expansion opens.
