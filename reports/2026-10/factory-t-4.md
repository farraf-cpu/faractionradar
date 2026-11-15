# Factory Orders prediction — target 2026-10-02 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-28T16:50:37.885816+00:00

## Final pick

**-0.1%** m/m Factory Orders (total manufacturers' new orders)

- Regime: modest contraction
- 68% CI: [-0.37%, +0.16%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.63%, +0.43%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend


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
| consensus | -0.10% | 0.30pp |
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

- **v1-simple-blend (2026-09-28)** — first ship.
