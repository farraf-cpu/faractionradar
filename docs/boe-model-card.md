# BOE Bank Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** Bank of England Bank Rate (MPC decision, ~8x/year, 12:00 UK time)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-boe.yml`

## What v2-outcome-distribution does

Emits both:
1. A scalar point estimate for the Bank Rate
2. A **probability distribution over discrete 25bp outcomes** (primary v2 upgrade)

Discretization: posterior point + sigma integrated over standard 25bp
buckets centered on outcome levels. Each bucket is +/- 0.125% wide
relative to its target level. Tail buckets extend to +/- infinity.

Output shape (`ourCall.outcomeDistribution`):
```json
{
  "hike50":     0.02,
  "hike25":     0.05,
  "hold":       0.80,
  "cut25":      0.12,
  "cut50":      0.01,
  "cut75_plus": 0.00,
  "modal":      "hold"
}
```

Rendered on `/calendar/pred/boe-<date>` as horizontal probability bars
with the modal outcome highlighted (same UI as FOMC + ECB v2).

Sub-models feeding the point + sigma:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| Current Bank Rate anchor | FRED `IUDSOIA` (SONIA overnight rate) | ~0.25 |

Inverse-MAE weighting: consensus dominates when present (5x tighter
MAE than anchor).

## Method notes

- **Normal-distribution assumption:** the discretization treats the
  posterior as `N(point, sigma^2)`. This is a proxy for a true Bayesian
  posterior — real sub-model errors are correlated and non-Gaussian.
- **Why IUDSOIA (SONIA):** FRED's `INTDSRGBM193N` (UK Discount Rate) is
  discontinued (frozen at 0.5% since 2013) and unusable. SONIA
  (Sterling Overnight Interbank Average) tracks BoE Bank Rate within
  ~5-10bp and updates daily.
- **No SONIA futures curve yet:** Phase 3.1 target — SONIA futures
  implied rate would replace or augment the current anchor.

## What v2 does NOT do (yet)

- **Empirical variance calibration** — sigma derived from sub-model
  MAE priors, not from historical resolutions.
- **SONIA futures curve integration** — deferred to v2.1.
- **Kalshi ladder for BoE outcomes** — Kalshi doesn't currently list
  BoE meeting outcomes; when they do, ladder-per-outcome would give
  direct market probabilities.

## Change log

- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 3 GBP
  expansion opens.
