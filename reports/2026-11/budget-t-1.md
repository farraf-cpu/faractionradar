# Monthly Treasury Budget prediction — target 2026-11-12 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-11T23:28:37.803905+00:00

## Final pick

**-$163.2B** federal surplus/deficit (Monthly Treasury Statement)

- Regime: wide monthly deficit
- 68% CI: [-$178.6B, -$147.7B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$194.0B, -$132.3B]
- Lean vs consensus: narrower deficit / larger surplus than consensus by $135.4B
- Sub-models used: consensus, anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 15.00 B |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | -$298.6B | $15.0B |
| anchor | +$197.9B | $40.0B |

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

- **v1-simple-blend (2026-11-11)** — first ship.
