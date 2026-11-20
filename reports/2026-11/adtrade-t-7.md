# Advance Goods Trade Balance prediction — target 2026-11-27 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-20T22:51:00.630162+00:00

## Final pick

**-$132.1B** advance goods trade balance

- Regime: extreme goods deficit
- 68% CI: [-$137.1B, -$127.1B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$142.1B, -$122.1B]
- Lean vs consensus: no consensus
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | $3.0B |
| anchor | -$132.1B | $5.0B |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
BOPGTB 3-month mean (Goods Trade Balance, Balance of Payments basis).

## Positioning

Goods-only trade balance released ~10 days ahead of the full Trade
Balance report. Advance report → market-moving import/export mix
signal for GDP nowcasts; the goods-services split lands with the
full report. Leading indicator on Q/Q GDP net-exports contribution.

## Change log

- **v1-simple-blend (2026-11-20)** — first ship.
