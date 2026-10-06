# Wholesale Inventories prediction — target 2026-10-08 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-06T21:28:14.956308+00:00

## Final pick

**+0.6%** m/m Wholesale Inventories

- Regime: wholesale buildup
- 68% CI: [+0.39%, +0.89%] · sigma source: prior (inverse-MAE)
- 95% CI: [+0.14%, +1.14%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.25 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.15pp |
| trend | +0.64% | 0.25pp |

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

- **v1-simple-blend (2026-10-06)** — first ship.
