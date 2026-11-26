# AU GDP prediction - target 2026-12-03 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-26T01:56:55.196108+00:00

## Final pick

**+0.5%** q/q AU GDP

- Regime: solid growth
- 68% CI: [+0.23%, +0.83%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.07%, +1.13%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.30 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.15pp |
| trend | +0.53% | 0.30pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
NGDPRSAXDCAUQ 4-qtr mean q/q trend.

## Positioning

Third Phase 5 AUD predictor. AU GDP q/q released quarterly by ABS
~9 weeks after quarter end at 11:30 AEDT.

## Change log

- **v1-simple-blend (2026-11-26)** - first ship. Phase 5 AUD expansion.
