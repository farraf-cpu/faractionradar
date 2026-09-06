# FOMC Predictor — Model Card

**Model version:** `v2.1-kalshi-ladder`
**Event:** FOMC federal funds target rate decision (~8 meetings/year)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-fomc.yml`

## What v2.1-kalshi-ladder does

Emits both:
1. A scalar point estimate (backward compat with v1)
2. A **probability distribution over discrete rate outcomes**, sourced
   from the Kalshi FED-DECISION contract ladder when available and
   falling back to a normal-CDF discretization otherwise.

Ladder mode: each 25bp bucket prob = `P(rate > lower_edge) - P(rate > upper_edge)`
computed via a step-below survival function over the ladder rungs
(rungs come in as `[(threshold, P(rate ≥ threshold))]`). Buckets are
renormalized to sum 1. The `source` field on the output distribution
indicates which path fired (`kalshi-ladder` or `gaussian-approx`).

Gaussian fallback (when ladder missing): posterior point + sigma is
integrated over standard 25bp buckets assuming N(point, sigma^2).
Same shape as pre-v2.1.

Output shape (`ourCall.outcomeDistribution`):
```json
{
  "hike50":     0.02,
  "hike25":     0.92,
  "hold":       0.05,
  "cut25":      0.00,
  "cut50":      0.00,
  "cut75_plus": 0.00,
  "modal":      "hike25"
}
```

Rendered on `/calendar/pred/fomc-<date>` as horizontal probability bars
with the modal outcome highlighted.

Sub-models feeding the point + sigma:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Kalshi prediction market | worker `/public/kalshi-implied` → `fomc.value_k` | ~0.05 |
| Bloomberg / FF consensus | worker `?read` if present (often blank for FOMC) | ~0.07 |
| Current fed funds anchor | FRED `DFEDTARU` (upper bound of target range) | ~0.25 |

Inverse-MAE weighting: markets dominate (5x tighter MAE than anchor).
Anchor + consensus provide fallback when markets are stale.

## Method notes

- **Normal-distribution assumption:** the discretization treats the
  posterior as `N(point, sigma^2)`. This is a proxy for a true Bayesian
  posterior — real sub-model errors are correlated and non-Gaussian, so
  distribution is directionally informative but should not be taken as
  a calibrated probability.
- **No policy-signal decomposition yet:** no dot-plot ingestion, no SEP
  integration, no speaker-hawkishness index. Distribution comes from
  discretizing the market-anchored blend.
- **Anchor only fallback:** if Kalshi + consensus both missing, anchor
  alone drives the distribution (typically peaks at hold with wide tails).

## What v2 does NOT do (yet)

- **Empirical variance calibration** — sigma is derived from sub-model
  MAE priors, not from historical resolutions. Blocked on live scoring
  accumulating enough data to calibrate.
- **Correlated-error handling** — sub-models draw from correlated data
  (Kalshi tracks futures which track SEP). Treating them independently
  over-weights information.
- **SEP + speaker signal** — dot-plot median from most recent SEP release
  and speaker-hawkishness rolling index would tighten distribution during
  transition meetings.

## Change log

- **v2.1-kalshi-ladder (2026-09-06)** — outcome distribution now sourced
  from the Kalshi ladder directly (step-below survival function over
  discrete rungs) when the ladder is present in `/public/kalshi-implied`.
  Falls back to Gaussian discretization when it isn't. Point estimate
  blend unchanged.
- **v2-outcome-distribution (2026-09-04)** — adds discrete outcome
  probability distribution over 25bp buckets. Same underlying blend as
  v1 for the point estimate; discretization is the upgrade.
- **v1-simple-blend (2026-09-03)** — three sub-model live blend. Kalshi
  implied + optional consensus + FRED anchor.
- **v1-beta (2026-09-01)** — placeholder shipped alongside NFP.
