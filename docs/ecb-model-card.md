# ECB Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** ECB Main Refinancing Rate (~8x/year, Governing Council meetings, 13:15 CET, ECB)
**Status:** Live (Phase 2, EUR expansion) - cadence T-7/4/3/2/1 + T-0 release-day refresh via `predict-ecb.yml`

## What v2-outcome-distribution does

Same pattern as FOMC v2: emits both a scalar point estimate and a
**probability distribution over discrete 25bp rate outcomes**.

Output shape (`ourCall.outcomeDistribution`):
```json
{
  "hike50":     0.07,
  "hike25":     0.24,
  "hold":       0.38,
  "cut25":      0.24,
  "cut50":      0.06,
  "cut75_plus": 0.01,
  "modal":      "hold"
}
```

Rendered on `/calendar/pred/ecb-<date>` with probability bars per bucket
and the modal outcome highlighted.

Sub-models feeding the point + sigma:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | worker `?read` if present | ~0.05 |
| FRED ECBDFR current-rate anchor | ECB Deposit Facility Rate | ~0.25 |

Inverse-MAE weighted. Consensus dominates when present (analysts
triangulate from ECB speaker comments + market pricing); anchor is
no-change baseline fallback.

## Positioning

First Phase 2 predictor (shipped 2026-09-04). ECB Governing Council
meets ~8x/year to set the Deposit Facility Rate (primary policy rate
since 2022). Distribution helps EUR traders size positions against
expected value across outcomes rather than a single point.

## What v2 does NOT do (yet)

- **Empirical variance calibration** — sigma is derived from sub-model
  MAE priors, not from historical resolutions.
- **Eurodollar/OIS futures integration** — CME markets are gated. When
  a free source is identified, adds a market-implied sub-model similar
  to FOMC's Kalshi input.
- **ECB speaker index** — a hawkishness rolling index over Governing
  Council member speeches since last meeting would tighten distribution
  during transition meetings.

## Change log

- **v2-outcome-distribution (2026-09-04)** — adds discrete outcome
  probability distribution over 25bp buckets. Same underlying blend
  as v1 for the point estimate.
- **v1-simple-blend (2026-09-04 earlier)** — first ship. Phase 2 EUR
  expansion opens with ECB, EurCPI, DE IFO trio.
