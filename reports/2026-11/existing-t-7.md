# Existing Home Sales prediction — target 2026-11-20 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-13T21:24:56.939967+00:00

## Final pick

**3883.33M** annualized existing home sales (SA)

- Regime: hot resale market
- 68% CI: [3883.25M, 3883.41M] · sigma source: prior (inverse-MAE)
- 95% CI: [3883.17M, 3883.49M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 50K |
| trend | 3883.33M | 80K |

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
