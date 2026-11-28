# Construction Spending prediction — target 2026-12-01 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-28T00:15:11.322019+00:00

## Final pick

**-0.0%** m/m Construction Spending (total, nominal)

- Regime: modest contraction
- 68% CI: [-0.41%, +0.39%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.81%, +0.79%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30pp |
| trend | -0.01% | 0.40pp |

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

- **v1-simple-blend (2026-11-28)** — first ship.
