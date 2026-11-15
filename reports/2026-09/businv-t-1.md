# Business Inventories prediction — target 2026-09-16 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-15T17:04:03.528614+00:00

## Final pick

**+0.5%** m/m Business Inventories (mfg + wholesale + retail combined)

- Regime: inventory buildup (weakening sales absorption)
- 68% CI: [+0.37%, +0.63%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.24%, +0.77%]
- Lean vs consensus: below consensus by 0.10pp
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.15 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.60% | 0.15pp |
| trend | +0.34% | 0.25pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
BUSINV 3-month m/m trend.

## Positioning

Combines manufacturers + wholesalers + retailers inventory levels.
Watched by GDP nowcasters — inventory-change is a direct component of
GDP. Sustained buildup (>0.5% m/m) signals slowing sales absorption
and often precedes production slowdowns. Inventory-to-sales ratio
(Phase 2 sub-model) sharpens the demand-vs-stock signal.

## Change log

- **v1-simple-blend (2026-09-15)** — first ship.
