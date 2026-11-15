# Philly Fed Manufacturing prediction — target 2026-09-17 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-13T15:53:05.684010+00:00

## Final pick

**+36.3** Philly Fed General Business Activity

- Regime: solid regional expansion
- 68% CI: [+32.9, +39.7] · sigma source: prior (inverse-MAE)
- 95% CI: [+29.5, +43.1]
- Lean vs consensus: above consensus by 7.4 pts
- Sub-models used: consensus, anchor


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
| consensus | +28.9 | 4.0 pts |
| anchor | +47.4 | 6.0 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
FRED trend sub-model deferred to v1.1 pending series-ID verification.

## Positioning

Second regional Fed survey each month (after Empire State). Together
with Empire, gives an early two-point read on national manufacturing
before the ISM survey lands 2-3 weeks later.

## Phase 2 targets

- **FRED trend sub-model** — verify correct Philly Fed general-activity FRED series ID and wire in
- **New Orders sub-index** — leads by 1-2 months
- **Empire + Philly composite** — average of the two as leading indicator for ISM Mfg

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 24th event covered.
