# S&P/Case-Shiller 20-City HPI prediction — target 2026-11-24 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-17T23:38:08.342511+00:00

## Final pick

**+2.4%** y/y S&P/Case-Shiller 20-City Composite HPI

- Regime: moderate appreciation
- 68% CI: [+2.17%, +2.67%] · sigma source: prior (inverse-MAE)
- 95% CI: [+1.92%, +2.92%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
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

- **v1-simple-blend (2026-11-17)** — first ship.
