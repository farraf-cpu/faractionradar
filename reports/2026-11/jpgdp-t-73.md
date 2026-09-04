# JP Preliminary GDP prediction - target 2026-11-16 (T-73)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T17:26:17.050141+00:00

## Final pick

**+0.2%** q/q JP Preliminary GDP

- Regime: flat / stall
- 68% CI: [+0.02%, +0.30%]
- 95% CI: [-0.12%, +0.44%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.20% | 0.15pp |
| trend | +0.08% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
NGDPRSAXDCJPQ 4-qtr mean q/q trend.

## Positioning

Third Phase 4 (JPY expansion) predictor. JP Preliminary GDP q/q
released ~45 days after quarter end at 08:50 JST by Cabinet Office.
Quarterly cadence — 4 fires/year.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 4 JPY expansion.
