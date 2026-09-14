# Empire State Manufacturing prediction — target 2026-09-15 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-14T15:52:54.277092+00:00

## Final pick

**+14.0** Empire State General Business Conditions

- Regime: solid regional expansion
- 68% CI: [+10.9, +17.2] · sigma source: prior (inverse-MAE)
- 95% CI: [+7.8, +20.3]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 4.00 pts |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +14.1 | 4.0 pts |
| trend | +14.0 | 5.0 pts |

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
