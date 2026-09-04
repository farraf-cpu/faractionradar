# CA Monthly GDP Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** CA Monthly GDP m/m (~60 day lag, 13:30 UTC, StatCan)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-cagdp.yml`

## What v1-simple-blend does

Consensus-only point estimate — StatCan monthly GDP by industry is
not on FRED cleanly.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "GDP m/m" CAD | ~0.15 |

Soft-skips when consensus missing.

## Positioning

Third Phase 6 CAD predictor. CA Monthly GDP by industry is the
key trader event for CAD — released monthly by StatCan.

## Caveats

FRED does not carry StatCan's monthly GDP by industry series
cleanly (searched CANMLGDPTOTLQINMEI, LORSGPTDCAM659S, CANGDPRSAQDS,
CANGDP1DSMEI, RGDPMICAM1S — all missing). Direct StatCan API
integration (statcan.gc.ca WDS API) deferred to v1.1.

## Change log

- **v1-simple-blend (2026-09-04)** - first ship. Phase 6 CAD expansion.
  Consensus-only pending StatCan API integration.
