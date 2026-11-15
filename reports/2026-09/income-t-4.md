# Personal Income prediction — target 2026-09-22 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-18T16:31:35.040388+00:00

## Final pick

**+0.4%** m/m Personal Income

- Regime: healthy income growth
- 68% CI: [+0.23%, +0.63%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.03%, +0.83%]
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
| trend | +0.43% | 0.20pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED PI
3-month trend (m/m %-change).

## Positioning

Nominal Personal Income (wages + salaries + transfers + rents + interest +
dividends). Released same day/time as PCE Price Index and Personal
Spending. The income-vs-spending gap is the household savings pulse the
Fed watches for consumption sustainability.

## Change log

- **v1-simple-blend (2026-09-18)** — first ship. 30th event covered; completes BEA income + outlays trio (Income + Spending + PCE Price).
