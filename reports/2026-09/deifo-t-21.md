# German IFO Business Climate prediction - target 2026-09-25 (T-21)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T11:21:04.162825+00:00

## Final pick

**-13.3** German IFO Business Climate Index

- Regime: sharp contraction
- 68% CI: [-14.8, -11.8]
- 95% CI: [-16.3, -10.3]
- Lean vs consensus: no consensus
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | - | 0.4 pts |
| anchor | -13.3 | 1.5 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + OECD
Composite Business Confidence for Germany (BCCICP02DEM460S) as
directional anchor.

## Caveats

IFO Institute's Business Climate Index is **proprietary** - not on FRED.
Anchor sub-model uses OECD composite business confidence for Germany,
which lags by ~2 months and uses a normalized (100=trend) scale different
from IFO's mid-80s to low-90s range. Anchor is thus a WEAK signal for the
next print, useful mainly as a directional check when consensus is
present. Phase 3 target: paid IFO API access or full HTML scrape.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Third Phase 2 EUR predictor. 3/3 EUR spec met.
