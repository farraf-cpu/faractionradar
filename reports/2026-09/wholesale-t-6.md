# Wholesale Inventories prediction — target 2026-09-10 (T-6)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T08:01:29.684208+00:00

## Final pick

**+0.4%** m/m Wholesale Inventories

- Regime: modest wholesale growth
- 68% CI: [+0.11%, +0.61%]
- 95% CI: [-0.14%, +0.86%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
| trend | +0.36% | 0.25pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
WHLSLRIMSA 3-month m/m trend.

## Positioning

Merchant wholesalers inventories — the leading sector in the
inventory-cycle chain. Full report ~day 9 (~1 week before Business
Inventories). Wholesalers absorb demand shocks first before feeding
back into mfg orders. Wholesale-to-sales ratio (Phase 2) is the
sharper signal for demand-vs-stock imbalance.

## Change log

- **v1-simple-blend (2026-09-04)** — first ship.
