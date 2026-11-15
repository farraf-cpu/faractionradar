# Consumer Credit prediction — target 2026-10-07 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-06T21:35:11.687939+00:00

## Final pick

**+$13.3B** m/m Consumer Credit change (Fed G.19)

- Regime: healthy borrowing
- 68% CI: [+$8.9B, +$17.6B] · sigma source: prior (inverse-MAE)
- 95% CI: [+$4.6B, +$22.0B]
- Lean vs consensus: below consensus by $1.1B
- Sub-models used: consensus, trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 5.00 B |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | +$14.4B | $5.0B |
| trend | +$11.5B | $8.0B |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
TOTALSL 3-month m/m trend (millions-to-billions).

## Positioning

Federal Reserve G.19 report. Combined revolving (credit cards) +
non-revolving (auto + student loans) consumer credit outstanding.
Volatile series — student-loan reclassifications and auto-loan seasonal
shifts can flip signs month-to-month. Revolving-credit sub-index
(Phase 2) is the cleaner consumer-confidence signal.

## Change log

- **v1-simple-blend (2026-10-06)** — first ship.
