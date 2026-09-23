# Advance Goods Trade Balance prediction — target 2026-09-30 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-23T16:54:58.234775+00:00

## Final pick

**-$109.3B** advance goods trade balance

- Regime: typical goods deficit
- 68% CI: [-$114.3B, -$104.3B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$119.3B, -$99.3B]
- Lean vs consensus: no consensus
- Sub-models used: anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 5.00 B |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | $3.0B |
| anchor | -$109.3B | $5.0B |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
BOPGTB 3-month mean (Goods Trade Balance, Balance of Payments basis).

## Positioning

Goods-only trade balance released ~10 days ahead of the full Trade
Balance report. Advance report → market-moving import/export mix
signal for GDP nowcasts; the goods-services split lands with the
full report. Leading indicator on Q/Q GDP net-exports contribution.

## Change log

- **v1-simple-blend (2026-09-23)** — first ship.
