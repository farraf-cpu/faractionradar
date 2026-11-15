# S&P/Case-Shiller 20-City HPI prediction — target 2026-09-29 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-25T16:47:07.136895+00:00

## Final pick

**+1.6%** y/y S&P/Case-Shiller 20-City Composite HPI

- Regime: moderate appreciation
- 68% CI: [+1.39%, +1.89%] · sigma source: prior (inverse-MAE)
- 95% CI: [+1.14%, +2.14%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.25 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
| trend | +1.64% | 0.25pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
SPCS20RSA 3-month y/y trend (12-month %-change).

## Positioning

S&P/Case-Shiller 20-City Composite Home Price Index. Reports 2-month
lag data (e.g. September release covers July). Trend is smooth so
FRED-anchor sub-model is competitive with consensus. Home-price
appreciation is the wealth-effect input for consumption forecasts
and a lagging read on shelter-inflation direction the Fed watches.

## Change log

- **v1-simple-blend (2026-09-25)** — first ship.
