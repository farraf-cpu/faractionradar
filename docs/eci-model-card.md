# Employment Cost Index Predictor — Model Card

**Model version:** `v1-simple-blend`
**Event:** US Employment Cost Index q/q (quarterly, ~end of month after quarter close, 08:30 ET, BLS)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-eci.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 16:35 UTC daily.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.05 |
| FRED ECIALLCIV last-print anchor | prior quarter q/q %-change | ~0.10 |

Value format: `+0.9%` q/q.

## Positioning

The Fed's cleanest wage-inflation read. Captures wages + benefits and
avoids composition bias that plagues Average Hourly Earnings from NFP.
Quarterly release means each print carries outsized weight in the policy
signal.

Regime bands:
- ≥1.1% — hot wage growth (persistent inflation risk)
- 0.8-1.1% — elevated
- 0.5-0.8% — moderate
- <0.5% — cooling

## Change log

- **v1-simple-blend** — first ship.
