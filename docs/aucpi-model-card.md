# AU CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** AU CPI y/y (quarterly, ~4-5 weeks after quarter end, 00:30 UTC / 11:30 AEDT, ABS)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-aucpi.yml`

## What v1-simple-blend does

Inverse-MAE-weighted point estimate over up to 2 sub-models. Quarterly
cadence — 4 fires/year.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` → matched FF `forecast` for "CPI y/y" AUD | ~0.15 |
| FRED CPALTT01AUQ659N previous-quarter | quarterly OECD "CPI: Total: Total for Australia" y/y series | ~0.30 |

## Positioning

Second Phase 5 AUD predictor. Australian CPI releases quarterly by
ABS (monthly indicator series exists but coverage is limited and not
the trader event). RBA target band is 2-3% CPI y/y.

## What v1 does NOT do (yet)

- **No trimmed-mean core CPI split** — RBA's preferred underlying gauge
  is trimmed-mean CPI (ABS series). Phase 5.1 target.
- **No monthly indicator sub-model** — ABS publishes a monthly CPI
  indicator with limited basket coverage; could serve as a leading
  signal but adds noise.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 5 AUD expansion.
