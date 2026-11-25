# New Home Sales prediction — target 2026-11-25 (T-0)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-25T23:40:02.281337+00:00

## Final pick

**656K** annualized new single-family home sales (SA)

- Regime: healthy new-home market
- 68% CI: [624K, 689K] · sigma source: prior (inverse-MAE)
- 95% CI: [591K, 722K]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 650K | 40K |
| trend | 665K | 55K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~40K) + FRED
HSN1F 3-month trend (~55K). New Home Sales is more rate-sensitive than
Existing — 90%+ of new-home purchases are mortgage-financed.

## Phase 2 targets

- **Mortgage rate 4-week lag** — Freddie Mac 30-yr fixed 4-week lag
  correlates ~-0.65 with new home sales (rate up → sales down after 1mo,
  faster reaction than existing)
- **NAHB Housing Market Index cross** — HMI is a builder-sentiment survey
  released ~5 days before New Home Sales; leading indicator
- **Housing Starts as trailing anchor** — Starts leads Sales by 3-6 months
  on the supply side (built homes take time to sell)

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 18th event covered.
