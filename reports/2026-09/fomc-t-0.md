# FOMC prediction — target 2026-09-17 (T-0)

**Model version:** `v2.1-kalshi-ladder`
**Published:** 2026-09-17T16:08:48.927280+00:00

## Final pick

**4.00%** target fed funds rate

- 68% CI: [3.94%, 4.06%] · sigma source: prior (inverse-MAE)
- 95% CI: [3.88%, 4.12%]
- Direction: hold expected (in line with current target)
- Sub-models used: market, anchor


## Outcome distribution (source: `kalshi-ladder`)

| Outcome | Probability |
|---------|-------------|
| +50bp hike | 1.5% |
| +25bp hike | 0.0% |
| hold | 46.0% |
| -25bp cut | 51.5% **(modal)** |
| -50bp cut | 0.0% |
| -75bp or deeper | 1.0% |


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
| anchor | 4.00% | 0.25 pp |

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
