# Initial Jobless Claims Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Initial Jobless Claims (weekly, every Thursday, 08:30 ET)
**Status:** Live — cadence T-2 + T-1 via `predict-claims.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend of consensus + FRED ICSA 4-week trend. Runs
weekly instead of monthly like the other predictors:

- Cadence: T-2 (Tuesday) + T-1 (Wednesday) only. No T-7/4/3 because
  weekly cadence means most information changes hands in the final 48h.
- Cron: daily 14:35 UTC. Gate script computes next-Thursday and exits
  on non-Tuesday/Wednesday days.

Sub-models:

| Sub-model | Source | Historical MAE (thousands of claims) |
|-----------|--------|--------------------------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~10 |
| FRED ICSA 4-week trend | mean of last 4 published ICSA values (Initial Claims, SA) | ~14 |

Weights are `1 / MAE`. Consensus dominates (~1.4x weight). Value format is
`225K` (whole thousand + K suffix).

## Regime annotation

Report tags include a loose labor-market regime label based on the level:
- < 200K: very tight labor market
- 200-240K: tight
- 240-280K: softening
- ≥ 280K: deteriorating

## Phase 2 target

- **Seasonal adjustment overlay** — Labor Day / MLK Day / July 4th weeks
  routinely produce +30-50K spikes that the standard SA under-adjusts for.
  Add a holiday-week detector that widens CI or applies a correction.
- **SAHM Rule cross-check** — if the 4-week trend is rising >0.5pp from
  the 12-month low, add a "labor-market deterioration flag" to the report.
- **Continuing Claims sub-model** — CCSA (Continuing Claims) leads Initial
  by ~1 week; useful for direction confirmation.

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 9th event covered.
  First weekly-cadence event (all prior are monthly).
