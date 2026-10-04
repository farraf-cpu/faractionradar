# Trade Balance prediction — target 2026-10-06 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-04T18:38:03.090164+00:00

## Final pick

**-$88.0B** trade balance (goods + services, SA)

- Regime: wide deficit
- 68% CI: [-$90.5B, -$85.6B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$92.9B, -$83.2B]
- Lean vs consensus: narrower deficit than consensus by $7.2B
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 3.00 B |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | -$95.2B | $3.0B |
| trend | -$78.5B | $4.0B |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~$3B MAE) +
FRED BOPGSTB 3-month trend (~$4B MAE). Trade balance is a component of
GDP (net exports contribution) so this predictor also feeds any Phase 2
GDPNow-style multi-signal work.

Phase 2 targets:
- **Advance Goods Trade Balance** — separate slug (goods-only, released
  ~1 week before Combined). Leads Combined by directional signal
- **Petroleum trade balance carve-out** — oil-price-driven swings distort
  headline. Split petroleum vs ex-petroleum
- **Dollar index cross** — DXY 3-month change correlates ~-0.4 with
  headline trade balance (stronger dollar = wider deficit); add as
  cross-check signal
