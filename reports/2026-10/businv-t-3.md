# Business Inventories prediction — target 2026-10-15 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-12T23:21:41.809141+00:00

## Final pick

**+0.4%** m/m Business Inventories (mfg + wholesale + retail combined)

- Regime: modest inventory growth
- 68% CI: [+0.28%, +0.55%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.15%, +0.68%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +0.40% | 0.15pp |
| trend | +0.45% | 0.25pp |

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

- **v1-simple-blend (2026-10-12)** — first ship.
