# Monthly Treasury Budget prediction — target 2026-10-16 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-15T20:21:43.935983+00:00

## Final pick

**-$119.3B** federal surplus/deficit (Monthly Treasury Statement)

- Regime: wide monthly deficit
- 68% CI: [-$134.7B, -$103.8B] · sigma source: prior (inverse-MAE)
- 95% CI: [-$150.1B, -$88.4B]
- Lean vs consensus: wider deficit / smaller surplus than consensus by $84.6B
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | -$34.7B | $15.0B |
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

- **v1-simple-blend (2026-10-15)** — first ship.
