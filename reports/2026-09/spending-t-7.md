# Personal Spending prediction — target 2026-09-22 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-15T16:24:02.205588+00:00

## Final pick

**+0.5%** m/m Personal Spending

- Regime: healthy consumer demand
- 68% CI: [+0.26%, +0.66%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.06%, +0.86%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
| trend | +0.46% | 0.20pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED PCE
3-month trend (m/m %-change).

## Positioning

Personal Consumption Expenditures (nominal). ~70% of US GDP is consumer
spending — this is the core consumer-demand pulse. Released same day/time
as PCE Price Index; the spending-vs-prices split is the "real-vs-nominal"
consumer read.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 29th event covered.
