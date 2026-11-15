# Housing Starts prediction — target 2026-09-17 (T-7)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-10T10:40:13.015677+00:00

## Final pick

**1.34M** annualized starts (SA)

- Regime: slowing construction cycle
- 68% CI: [1.29M, 1.38M] · sigma source: prior (inverse-MAE)
- 95% CI: [1.25M, 1.43M]
- Lean vs consensus: no consensus
- Sub-models used: trend, permits_leading


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 60 K |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 40K |
| trend | 1.28M | 60K |
| permits_leading | 1.41M | 70K |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 3 sub-models —
consensus (~40K MAE) + FRED HOUST 3-month trend (~60K MAE) + FRED PERMIT
3-month trend (~70K MAE). Housing Starts is trend-persistent so a short
3-month window captures direction changes; permits legally precede
starts by 1-2 months. Backtest run 34099012259 confirmed proper
inverse-MAE blend of HOUST + PERMIT gives +8.7% MAE reduction vs
HOUST alone.

Phase 2 targets:
- **Mortgage rate cross** — Freddie Mac 30-year fixed (FRED MORTGAGE30US)
  is the main driver of Starts turns. Add a mortgage-rate-change sub-model
  that flags direction when the 4-week average moves >25bp
- **Regional split** — Northeast/Midwest/South/West follow different
  seasonal patterns; South is ~50% of national starts

## Change log

- **v1.1-simple-blend (2026-09-07, backtest-verified)** — added FRED
  PERMIT 3-mo trend as third sub-model. Inverse-MAE blend at w~0.68
  HOUST + w~0.32 PERMIT. Backtest run 34099012259 confirmed +8.7%
  MAE reduction vs v1. Falls through cleanly on FRED failure.
  Supersedes reverted earlier same-day ship (SHA 93f30ec) where
  backtest architecture bug (measured PERMIT alone) showed spurious
  regression.
- **v1-simple-blend** — first ship.
