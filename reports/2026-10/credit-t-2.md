# Consumer Credit prediction — target 2026-10-07 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-05T23:07:34.818796+00:00

## Final pick

**+$13.9B** m/m Consumer Credit change (Fed G.19)

- Regime: healthy borrowing
- 68% CI: [+$9.6B, +$18.3B] · sigma source: prior (inverse-MAE)
- 95% CI: [+$5.2B, +$22.6B]
- Lean vs consensus: below consensus by $1.5B
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
| consensus | +$15.4B | $5.0B |
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

- **v1-simple-blend (2026-10-05)** — first ship.
