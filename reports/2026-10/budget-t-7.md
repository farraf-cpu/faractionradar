# Monthly Treasury Budget prediction — target 2026-10-13 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-06T21:38:36.200165+00:00

## Final pick

**-$344.8B** federal surplus/deficit (Monthly Treasury Statement)

- Regime: extreme monthly deficit
- 68% CI: [-$384.8B, -$304.8B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$424.8B, -$264.8B]
- Lean vs consensus: no consensus
- Sub-models used: anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 40.00 B |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | $15.0B |
| anchor | -$344.8B | $40.0B |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
MTSDS133FMS same-month-last-year anchor. Year-ago is preferred over
3-mo mean because of strong quarterly tax-payment seasonality
(April surplus, Sep/Jan/Jun corporate quarterly payments).

## Positioning

Federal fiscal balance the market watches for Treasury supply guidance
and Fed liquidity effects. Wide deficits (< -$200B) pressure Treasury
issuance; surprising surpluses (rare, tax-season only) reduce
near-term supply. Debt-ceiling episodes make this print market-moving.

## Change log

- **v1-simple-blend (2026-10-06)** — first ship.
