# FOMC Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** FOMC federal funds target rate decision (~8 meetings/year)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-fomc.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate of the target fed funds rate. Publishes
as a scalar rate (e.g. `4.25%`) — a simplification of what's really a
distribution over discrete outcomes (hold / cut25 / cut50 / hike25).
Phase 2 target: publish the full outcome distribution.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Kalshi prediction market | live from calendar-worker `/public/kalshi-implied` → `fomc.value_k` (interpolated rate) | ~0.05 |
| Bloomberg / FF consensus | live from calendar-worker `?read` if present (often blank for FOMC) | ~0.07 |
| Current fed funds anchor | FRED `DFEDTARU` (upper bound of current target range) | ~0.25 |

Weights are `1 / MAE`. In practice this makes markets dominate: their
0.05pp MAE is 5x tighter than the anchor's 0.25pp, so market weight is ~5x
larger. That matches the empirical observation that fed funds futures and
Kalshi have called every FOMC decision within a rounding error since 2015.

Anchor is included only so the emitter never returns zero — if markets fail
and consensus is blank, "no change from current target" is a defensible
fallback.

## What v1-simple-blend is NOT

- **Not a probability distribution.** Just a scalar. The real prediction on
  rate-decision day is a distribution over ~5 discrete outcomes; a scalar
  point estimate collapses information. Phase 2 fixes this.
- **Not a policy-signal decomposition.** No Fed speaker index, no dot-plot
  ingestion, no SEP integration. The scalar is Kalshi + a fallback; the
  value-add above pure market data is minimal at this version.
- **Not tuned to volatility regime.** FOMC MAE is very low during holds and
  wider during transition meetings. Weights are static across regimes.

## Phase 2 target: v2-outcome-distribution

Discrete-outcome Bayesian model publishing a probability distribution:

- Prediction markets (Kalshi + Polymarket, if we clear the geo-block)
- Fed funds futures implied probability distribution (CME)
- SEP dot-plot median (from most recent SEP release)
- Speaker-hawkishness rolling index (Fed speeches since last meeting)
- Data surprise index (CPI + NFP + PCE surprises since last meeting)

Payload becomes `outcomeDistribution: {hold: 0.85, cut25: 0.12, cut50: 0.03}`
plus a `modalOutcome` string and a scalar-collapsed `value` for
backwards-compat with the current schema.

## Change log

- **v1-simple-blend (2026-09-03)** — three sub-model live blend. Kalshi
  implied + optional consensus + FRED anchor. First FOMC prediction fires
  for Sep 17 event on T-7 (2026-09-10).
- **v1-beta (2026-09-01)** — placeholder shipped alongside NFP. Superseded.
