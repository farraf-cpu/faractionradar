# Business Inventories prediction — target 2026-11-17 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-15T21:25:30.019910+00:00

## Final pick

**+0.5%** m/m Business Inventories (mfg + wholesale + retail combined)

- Regime: modest inventory growth
- 68% CI: [+0.36%, +0.62%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.22%, +0.75%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.50% | 0.15pp |
| trend | +0.47% | 0.25pp |

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

- **v1-simple-blend (2026-11-15)** — first ship.
