# Personal Spending prediction — target 2026-11-24 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-17T00:12:28.038913+00:00

## Final pick

**+0.5%** m/m Personal Spending

- Regime: healthy consumer demand
- 68% CI: [+0.34%, +0.74%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.14%, +0.94%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.20 pp |
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
| trend | +0.54% | 0.20pp |

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
