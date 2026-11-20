# Personal Income prediction — target 2026-11-24 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-20T22:43:05.663288+00:00

## Final pick

**+0.3%** m/m Personal Income

- Regime: flat income growth
- 68% CI: [+0.08%, +0.48%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.12%, +0.68%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
| trend | +0.28% | 0.20pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED PI
3-month trend (m/m %-change).

## Positioning

Nominal Personal Income (wages + salaries + transfers + rents + interest +
dividends). Released same day/time as PCE Price Index and Personal
Spending. The income-vs-spending gap is the household savings pulse the
Fed watches for consumption sustainability.

## Change log

- **v1-simple-blend (2026-11-20)** — first ship. 30th event covered; completes BEA income + outlays trio (Income + Spending + PCE Price).
