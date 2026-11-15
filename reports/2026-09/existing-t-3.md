# Existing Home Sales prediction — target 2026-09-22 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-19T15:21:39.747185+00:00

## Final pick

**4056.67M** annualized existing home sales (SA)

- Regime: hot resale market
- 68% CI: [4056.59M, 4056.75M] · sigma source: prior (inverse-MAE)
- 95% CI: [4056.51M, 4056.83M]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.08 M |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 50K |
| trend | 4056.67M | 80K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~50K MAE) + FRED
EXHOSLUSM495S 3-month trend (~80K MAE). Existing home sales tracks the
resale market — different signal than Housing Starts (new construction).

## Phase 2 targets

- **Mortgage rate lag** — Freddie Mac 30-yr fixed 8-week lag correlates
  ~-0.6 with existing sales (rate up → sales down after 2mo)
- **Pending Home Sales cross** — NAR Pending Home Sales leads Existing
  by 1-2 months as a same-shop earnings-like leading indicator
- **Regional decomposition** — Northeast/Midwest/South/West follow
  different seasonal patterns; South is ~45% of national

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 17th event covered.
