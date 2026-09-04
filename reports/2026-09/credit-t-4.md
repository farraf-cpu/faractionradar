# Consumer Credit prediction — target 2026-09-08 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:11:51.262743+00:00

## Final pick

**+$11.0B** m/m Consumer Credit change (Fed G.19)

- Regime: healthy borrowing
- 68% CI: [+$3.0B, +$19.0B]
- 95% CI: [-$5.0B, +$27.0B]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | $5.0B |
| trend | +$11.0B | $8.0B |

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

- **v1-simple-blend (2026-09-04)** — first ship.
