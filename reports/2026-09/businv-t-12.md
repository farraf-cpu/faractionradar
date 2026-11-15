# Business Inventories prediction — target 2026-09-16 (T-12)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:52:06.269269+00:00

## Final pick

**+0.3%** m/m Business Inventories (mfg + wholesale + retail combined)

- Regime: modest inventory growth
- 68% CI: [+0.09%, +0.59%]
- 95% CI: [-0.16%, +0.84%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
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

- **v1-simple-blend (2026-09-04)** — first ship.
