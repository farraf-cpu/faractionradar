# UMich Consumer Sentiment prediction — target 2026-09-11 (T-0)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-11T15:32:28.792350+00:00

## Final pick

**50.3** index

- Regime: recession-level sentiment
- 68% CI: [49.1, 51.6] · sigma source: prior (inverse-MAE)
- 95% CI: [47.8, 52.9]
- Lean vs consensus: below consensus by 0.7 pts
- Sub-models used: consensus, trend, oil_shock


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 1.50 pts |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 51.0 | 1.5 pts |
| trend | 49.8 | 2.5 pts |
| oil_shock | 49.5 | 3.5 pts |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 3 sub-models —
consensus (~1.5 pts MAE) + FRED UMCSENT 3-month trend (~2.5 pts MAE) +
FRED MCOILWTICO m/m oil-shock adjustment (~3.5 pts MAE, conservative
pre-empirical weight). Unlike CB Consumer Confidence, UMCSENT is freely
published on FRED — enables real trend sub-model.

Oil-shock sub-model applies `OIL_SHOCK_COEFF = -0.068` pts of UMich
decline per 1% MCOILWTICO m/m increase to the trend baseline.
Backtest-fit from OLS refit on 24 releases (backtest run 34099012259).
First ship 2026-09-07 used -0.4 which was ~6x too large; refit closes
that gap. Sign confirmed by empirical data (oil up -> sentiment down
via gas-price transmission).

## Relationship to CB Consumer Confidence

Correlates ~0.75 with CB Confidence but releases 2-3 weeks earlier
(preliminary comes mid-month vs CB's last Tuesday). Often a leading
indicator for CB Confidence direction changes.

## Phase 2 targets

- **Inflation Expectations sub-index** — UMich publishes 1-year and 5-year
  inflation expectations as sub-indices. Fed watches these; separate slug
  in Phase 2
- **Preliminary vs Revised split** — Revised release comes end-of-month
  with sample doubled. Add separate slug `umich-revised-<date>`
- **Weekly sentiment cross** — Bloomberg Weekly Consumer Comfort as high-
  frequency leading input

## Change log

- **v1.1-simple-blend (2026-09-07, refit)** — added MCOILWTICO m/m
  oil-shock sub-model with backtest-fit coefficient -0.068 (from
  backtest run 34099012259, 24-release OLS refit). Falls through
  cleanly when FRED fetch fails or trend baseline is unavailable.
  Supersedes earlier same-day ship (SHA 4909e1e) that used -0.4
  which the backtest showed was ~6x too large.
- **v1-simple-blend (2026-09-03)** — first ship. 19th event covered.
  Covers Preliminary only; Revised is Phase 2.
