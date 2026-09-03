# Housing Starts prediction — target 2026-09-17 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T12:06:48.850497+00:00

## Final pick

**1.28M** annualized starts (SA)

- Regime: slowing construction cycle
- 68% CI: [1.22M, 1.34M]
- 95% CI: [1.16M, 1.40M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 40K |
| trend | 1.28M | 60K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~40K MAE) + FRED
HOUST 3-month trend (~60K MAE). Housing Starts is trend-persistent so a
short 3-month trend window captures direction changes.

Phase 2 targets:
- **Building Permits leading indicator** — FRED PERMIT publishes same day
  as Starts; use as a co-anchor rather than trend-alone
- **Mortgage rate cross** — Freddie Mac 30-year fixed (FRED MORTGAGE30US)
  is the main driver of Starts turns. Add a mortgage-rate-change sub-model
  that flags direction when the 4-week average moves >25bp
- **Regional split** — Northeast/Midwest/South/West follow different
  seasonal patterns; South is ~50% of national starts
