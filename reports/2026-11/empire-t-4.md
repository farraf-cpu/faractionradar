# Empire State Manufacturing prediction — target 2026-11-16 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-12T21:55:37.541924+00:00

## Final pick

**+17.9** Empire State General Business Conditions

- Regime: solid regional expansion
- 68% CI: [+12.9, +22.9] · sigma source: prior (inverse-MAE)
- 95% CI: [+7.9, +27.9]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 4.0 pts |
| trend | +17.9 | 5.0 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~4 pts) + FRED
GACDISA066MSFRBNY 3-mo trend (~5 pts). Empire State releases ~15th of
month — first regional Fed survey ahead of ISM Manufacturing on the 1st
business day of the following month.

## Positioning

Empire State is one of five regional Fed manufacturing surveys (Empire,
Philly, Dallas, Kansas City, Richmond). Weighted composite of the five
correlates ~0.85 with ISM Mfg headline. Empire is the earliest to publish
each month, so it's the leading edge of the regional composite signal.

## Phase 2 targets

- **New Orders sub-index** — Empire's New Orders leads national manufacturing
  by 1-2 months
- **Feed into ismmfg predictor** — as a leading sub-model alongside Chicago PMI

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 23rd event covered.
