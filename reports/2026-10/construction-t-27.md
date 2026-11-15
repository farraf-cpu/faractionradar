# Construction Spending prediction — target 2026-10-01 (T-27)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:58:17.002463+00:00

## Final pick

**-0.2%** m/m Construction Spending (total, nominal)

- Regime: modest contraction
- 68% CI: [-0.56%, +0.24%]
- 95% CI: [-0.96%, +0.64%]
- Lean vs consensus: no consensus
- Sub-models used: trend

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

- **v1-simple-blend (2026-09-04)** — first ship.
