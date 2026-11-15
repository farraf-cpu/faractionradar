# S&P/Case-Shiller 20-City HPI prediction — target 2026-09-29 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-27T16:44:38.958383+00:00

## Final pick

**+2.0%** y/y S&P/Case-Shiller 20-City Composite HPI

- Regime: moderate appreciation
- 68% CI: [+1.86%, +2.12%] · sigma source: prior (inverse-MAE)
- 95% CI: [+1.72%, +2.25%]
- Lean vs consensus: below consensus by 0.21pp
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
| consensus | +2.20% | 0.15pp |
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

- **v1-simple-blend (2026-09-27)** — first ship.
