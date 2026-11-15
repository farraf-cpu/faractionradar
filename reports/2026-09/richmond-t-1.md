# Richmond Fed Manufacturing prediction — target 2026-09-22 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-21T16:14:42.557524+00:00

## Final pick

**+4.6** Richmond Fed Composite Index

- Regime: modest Mid-Atlantic expansion
- 68% CI: [+0.5, +8.7] · sigma source: prior (inverse-MAE)
- 95% CI: [-3.7, +12.8]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 5.00 pts |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +5.0 | 5.0 pts |
| anchor | +4.0 | 7.0 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
FRED trend sub-model deferred to v1.1 pending series-ID verification.

## Positioning

Fifth and final regional Fed survey each month — completes the 5-Fed
composite proxy for ISM Mfg (Empire + Philly + Dallas + KC + Richmond).
5th district covers Mid-Atlantic: VA, MD, NC, SC, WV.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 27th event covered.
