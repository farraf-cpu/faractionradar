# JP Preliminary GDP prediction - target 2026-11-16 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-12T23:43:43.117802+00:00

## Final pick

**+0.1%** q/q JP Preliminary GDP

- Regime: flat / stall
- 68% CI: [-0.16%, +0.44%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.46%, +0.74%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +0.14% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
NGDPRSAXDCJPQ 4-qtr mean q/q trend.

## Positioning

Third Phase 4 (JPY expansion) predictor. JP Preliminary GDP q/q
released ~45 days after quarter end at 08:50 JST by Cabinet Office.
Quarterly cadence — 4 fires/year.

## Change log

- **v1-simple-blend (2026-11-12)** - first ship. Phase 4 JPY expansion.
