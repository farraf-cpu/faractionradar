# Monthly Treasury Budget prediction — target 2026-09-11 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:15:57.995649+00:00

## Final pick

**-$291.1B** federal surplus/deficit (Monthly Treasury Statement)

- Regime: wide monthly deficit
- 68% CI: [-$331.1B, -$251.1B]
- 95% CI: [-$371.1B, -$211.1B]
- Lean vs consensus: no consensus
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | $15.0B |
| anchor | -$291.1B | $40.0B |

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

- **v1-simple-blend (2026-09-04)** — first ship.
