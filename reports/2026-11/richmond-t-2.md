# Richmond Fed Manufacturing prediction — target 2026-11-24 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-22T21:37:39.072548+00:00

## Final pick

**-2.6** Richmond Fed Composite Index

- Regime: modest Mid-Atlantic contraction
- 68% CI: [-6.7, +1.5] · sigma source: prior (inverse-MAE)
- 95% CI: [-10.8, +5.7]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | -3.0 | 5.0 pts |
| anchor | -2.0 | 7.0 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
FRED trend sub-model deferred to v1.1 pending series-ID verification.

## Positioning

Fifth and final regional Fed survey each month — completes the 5-Fed
composite proxy for ISM Mfg (Empire + Philly + Dallas + KC + Richmond).
5th district covers Mid-Atlantic: VA, MD, NC, SC, WV.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 27th event covered.
