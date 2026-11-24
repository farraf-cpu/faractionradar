# Consumer Confidence prediction — target 2026-11-24 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-24T23:47:18.299586+00:00

## Final pick

**92.2** index (1985 = 100)

- Regime: cautious confidence
- 68% CI: [90.3, 94.1] · sigma source: prior (inverse-MAE)
- 95% CI: [88.4, 95.9]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 92.4 | 2.0 pts |
| anchor | 91.7 | 4.0 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
Conference Board's index is proprietary (analogous to ISM PMI) so no
FRED trend sub-model in v1. Same architecture as ISM Manufacturing/Services
predictors.

## Phase 2 target

- **University of Michigan Consumer Sentiment (UMCSENT)** — FRED-published
  free, releases mid-month (preliminary) and end-of-month (revised),
  correlates ~0.75 with Conference Board's Consumer Confidence
- **Weekly consumer sentiment surveys** — Bloomberg Weekly Consumer
  Comfort, Redfin Homebuyer Demand — build weighted composite as leading
  indicator for CB
- **Sub-index decomposition** — Present Situation vs Expectations
  components diverge in inflection months; publish both

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 15th event covered.
