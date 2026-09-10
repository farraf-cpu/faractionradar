# FOMC prediction — target 2026-09-17 (T-7)

**Model version:** `v2.1-kalshi-ladder`
**Published:** 2026-09-10T14:16:32.688849+00:00

## Final pick

**3.96%** target fed funds rate

- 68% CI: [3.90%, 4.02%] · sigma source: prior (inverse-MAE)
- 95% CI: [3.84%, 4.08%]
- Direction: +21bp move vs current expected
- Sub-models used: market, anchor


## Outcome distribution (source: `kalshi-ladder`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 0.5% |
| +25bp hike | 1.0% |
| hold | 53.0% **(modal)** |
| -25bp cut | 45.0% |
| -50bp cut | 0.0% |
| -75bp or deeper | 0.5% |


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.05 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| market | 4.00% | 0.05 pp |
| consensus | — | 0.07 pp |
| anchor | 3.75% | 0.25 pp |

## Method

v2.1-kalshi-ladder: point estimate is an inverse-MAE-weighted mean of
market + consensus + anchor sub-models. The outcome distribution over
hike50 / hike25 / hold / cut25 / cut50 / cut75+ is derived directly from
the Kalshi FED-DECISION contract ladder when available (source =
kalshi-ladder), falling back to a normal-CDF approximation of the point
+ sigma when no ladder is present (source = gaussian-approx).

Ladder path: each bucket prob = P(rate > lower_edge) - P(rate > upper_edge)
via a step-below survival function over discrete ladder rungs, then
renormalized to sum 1. This gives the market's actual per-outcome pricing
instead of assuming Gaussian residuals — meaningful for rate-cut skew events.
