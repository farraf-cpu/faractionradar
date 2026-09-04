# UMich Consumer Sentiment prediction — target 2026-09-11 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T15:32:31.165193+00:00

## Final pick

**49.8** index

- Regime: recession-level sentiment
- 68% CI: [47.3, 52.3]
- 95% CI: [44.8, 54.8]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 1.5 pts |
| trend | 49.8 | 2.5 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~1.5 pts MAE) +
FRED UMCSENT 3-month trend (~2.5 pts MAE). Unlike CB Consumer Confidence,
UMCSENT is freely published on FRED — enables real trend sub-model.

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

- **v1-simple-blend (2026-09-03)** — first ship. 19th event covered.
  Covers Preliminary only; Revised is Phase 2.
