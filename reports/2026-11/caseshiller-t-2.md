# S&P/Case-Shiller 20-City HPI prediction — target 2026-11-24 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-22T21:58:42.997221+00:00

## Final pick

**+2.6%** y/y S&P/Case-Shiller 20-City Composite HPI

- Regime: moderate appreciation
- 68% CI: [+2.46%, +2.73%] · sigma source: prior (inverse-MAE)
- 95% CI: [+2.33%, +2.86%]
- Lean vs consensus: below consensus by 0.10pp
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +2.70% | 0.15pp |
| trend | +2.42% | 0.25pp |

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

- **v1-simple-blend (2026-11-22)** — first ship.
