# Trade Balance prediction — target 2026-12-04 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-27T23:24:40.493496+00:00

## Final pick

**-$101.2B** trade balance (goods + services, SA)

- Regime: extreme deficit
- 68% CI: [-$105.2B, -$97.2B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$109.2B, -$93.2B]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | $3.0B |
| trend | -$101.2B | $4.0B |

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
