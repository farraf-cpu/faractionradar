# Factory Orders prediction — target 2026-10-02 (T-28)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:56:43.455117+00:00

## Final pick

**-0.1%** m/m Factory Orders (total manufacturers' new orders)

- Regime: modest contraction
- 68% CI: [-0.61%, +0.39%]
- 95% CI: [-1.11%, +0.89%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30pp |
| trend | -0.11% | 0.50pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
AMTMNO 3-month trend.

## Positioning

Full M3 Survey report from Census — adds nondurable orders + revised
durables + inventories on top of the advance Durable Goods print
already released ~5-7 business days earlier. Aircraft-order cycles
make headline volatile; ex-transportation is the cleaner signal
(Phase 2 sub-model).

## Change log

- **v1-simple-blend (2026-09-04)** — first ship.
