# Construction Spending prediction — target 2026-10-01 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-24T16:51:52.127624+00:00

## Final pick

**-0.2%** m/m Construction Spending (total, nominal)

- Regime: modest contraction
- 68% CI: [-0.56%, +0.24%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.96%, +0.64%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.40 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30pp |
| trend | -0.16% | 0.40pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
TTLCONS 3-month m/m trend.

## Positioning

Nominal outlays across residential + nonresidential + public
construction. 2-month data lag makes trend competitive with consensus.
Residential-vs-nonresidential split (Phase 2) is where the leading
signal lives — housing pipeline vs manufacturing/infra pipeline
diverge under different macro regimes.

## Change log

- **v1-simple-blend (2026-09-24)** — first ship.
