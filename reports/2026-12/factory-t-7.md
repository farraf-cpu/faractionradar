# Factory Orders prediction — target 2026-12-03 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-26T00:38:23.879291+00:00

## Final pick

**+1.0%** m/m Factory Orders (total manufacturers' new orders)

- Regime: modest expansion
- 68% CI: [+0.48%, +1.48%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.02%, +1.98%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.30pp |
| trend | +0.98% | 0.50pp |

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

- **v1-simple-blend (2026-11-26)** — first ship.
