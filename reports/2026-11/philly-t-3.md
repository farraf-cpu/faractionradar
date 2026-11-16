# Philly Fed Manufacturing prediction — target 2026-11-19 (T-3)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-16T23:52:10.280255+00:00

## Final pick

**+19.9** Philly Fed General Business Activity

- Regime: solid regional expansion
- 68% CI: [+16.5, +23.3] · sigma source: prior (inverse-MAE)
- 95% CI: [+13.1, +26.7]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +19.2 | 4.0 pts |
| anchor | +20.9 | 6.0 pts |

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
