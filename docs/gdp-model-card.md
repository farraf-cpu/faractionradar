# GDP Advance Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US GDP Advance estimate (quarterly, ~30 days after quarter-end, 08:30 ET)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-gdp.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED GDP 4-quarter trend.

Sub-models:

| Sub-model | Source | Historical MAE (pp on SAAR) |
|-----------|--------|-----------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.3 |
| FRED A191RL1Q225SBEA 4-quarter trend | mean of last 4 published Real GDP q/q %-change SAAR values | ~0.5 |

## Value format

Percentage-change SAAR (Seasonally Adjusted Annualized Rate), one decimal,
signed: `+2.5%`. Regime annotation on report:
- ≥ 3.0%: above-trend expansion
- 2.0-3.0%: trend growth (US potential ~1.8-2.0%)
- 1.0-2.0%: sub-trend growth
- 0.0-1.0%: stagnation risk
- < 0.0%: contraction

## Why quarterly cadence matters

Only 4 releases per year — every prediction is high-stakes for the public
track record. Errors are more visible; misses are memorable. Consensus is
also tighter than for monthly events because analysts spend the full
quarter modeling GDP component contributions.

## Phase 2 target — Atlanta Fed GDPNow

GDPNow is the gold-standard leading indicator for GDP Advance. Atlanta Fed
publishes it every ~3 days from ~1 month before release, updated as
component data (Retail Sales, Housing Starts, Trade Balance, ISM, etc.)
prints. Final GDPNow MAE is ~0.3-0.4pp — competitive with consensus.

Wire via Atlanta Fed's public JSON tracker. Would tighten our blend from
~0.3pp to ~0.2-0.25pp when read in the final week before release.

Other Phase 2 candidates:
- **NY Fed Nowcasting Report** (weekly) — independent 2nd nowcast for cross-check
- **BEA Advance vs Second Estimate revision history** — quantify how much
  Advance typically gets revised, and by how much, for CI calibration

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 11th event covered.
  Final event on the initial US top-tier coverage list.
