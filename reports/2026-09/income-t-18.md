# Personal Income prediction — target 2026-09-22 (T-18)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:22:19.286616+00:00

## Final pick

**+0.4%** m/m Personal Income

- Regime: healthy income growth
- 68% CI: [+0.23%, +0.63%]
- 95% CI: [+0.03%, +0.83%]
- Lean vs consensus: no consensus
- Sub-models used: trend

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

- **v1-simple-blend (2026-09-04)** — first ship. 30th event covered; completes BEA income + outlays trio (Income + Spending + PCE Price).
