# Phase 26 learnings — v2.1-wide-buckets for CBRT + BCB (Rule 36 fix)

Phase 26 opened 2026-09-05 (post-country-expansion quality phase).
First upgrade phase (not country expansion). Country coverage
unchanged at 25.

## What changed

**CBRT (Turkey) v2.1:** 100bp buckets
- Was: hike50/hike25/hold/cut25/cut50/cut75_plus (25bp grid)
- Now: hike200/hike100/hold/cut100/cut200/cut300_plus (100bp grid)
- Smoke: -236bp cut lean → cut200 modal 99% (was cut75_plus 62% in v2)

**BCB (Brazil) v2.1:** 50bp buckets
- Was: hike50/hike25/hold/cut25/cut50/cut75_plus (25bp grid)
- Now: hike100/hike50/hold/cut50/cut100/cut150_plus (50bp grid)
- Smoke: -86bp cut lean → cut100 modal 96% (was cut25+cut50 mix in v2)

Both point estimates unchanged; only `compute_outcome_distribution`
grid width was tuned per central bank's typical move size.

## Rule 36 fully implemented

Original Rule 36 statement (Phase 17): "For predictors where typical
move size > 50bp, either (a) widen buckets to match, (b) drop outcome
distribution and use point estimate only, or (c) note in model card."

Phase 26 chose (a). Per-country bucket width tuned:
- CBRT: 100bp (moves 100-250bp)
- BCB: 50bp (moves 25-100bp)
- FOMC/ECB/BOE/BOJ/RBA/BOC/RBNZ/SNB/Riksbank/etc: 25bp (unchanged)

Standard 25bp grid still default for DM central banks. Wide-bucket
variant only shipped where necessary.

## Worker registry updates

- `bcb-v2-outcome-distribution` → `bcb-v2.1-wide-buckets`
- `cbrt-v2-outcome-distribution` → `cbrt-v2.1-wide-buckets`
- Cadence + method text + phase_2_target refreshed

## Ledger

Predictor: a864749. Worker: (see next commit).

## Remaining quality upgrades (deferred)

- **True Bayesian calibration** — still blocked on live resolutions
  accumulating. Q4 2026 target as Phase 1 US predictors clear
  their first ~50 events.
- **JP e-Stat integration** — exemplar for non-FRED anchor pattern.
  Would upgrade jpcpi v1 → v1.1 with real trend anchor. ~1h build.
- **UI Country/Category filters** — Vega's territory.
- **Kalshi ladder-per-outcome integration** — market-implied
  probabilities for rate decisions instead of discretized point.

## Country + quality summary post-Phase 26

- 25 currency areas (24 non-USD expansions across 2 days)
- 118 predictors total
- 2 predictors upgraded to v2.1-wide-buckets (Rule 36)
- 38 unique rules learned across phases 2-26
- Session cost trajectory: Phase 2 4-6h → Phases 3-26 30min each
