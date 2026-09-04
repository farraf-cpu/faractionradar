# German IFO Business Climate Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** German IFO Business Climate Index (monthly, ~25th, 09:00 CET, IFO Institute)
**Status:** Live (Phase 2, EUR expansion) - cadence T-7/4/3/2/1 via `predict-deifo.yml`

## What v1-simple-blend does

Inverse-MAE-weighted blend. Cron 17:55 UTC daily.

| Sub-model | Source | Historical MAE (pts) |
|-----------|--------|----------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.4 |
| FRED BCCICP02DEM460S 3-mo mean anchor | OECD Composite Business Confidence, Germany | ~1.5 |

Value format: `88.6` (index level, one decimal). Typical range 80-105.

## Positioning

Third Phase 2 predictor. IFO Business Climate is Germany's leading
sentiment indicator - Bundesbank + ECB watch it closely as a Eurozone
growth leading signal.

## Caveats

IFO Institute's Business Climate Index is **proprietary** - not on FRED.
Anchor sub-model uses OECD composite business confidence for Germany,
which lags by ~2 months and uses a normalized (100=trend) scale different
from IFO's mid-80s to low-90s range. Anchor is thus a WEAK signal for the
next print, useful mainly as a directional check when consensus is
present. Phase 3 target: paid IFO API access or full HTML scrape.

## Change log

- **v1-simple-blend** - first ship. Third Phase 2 EUR predictor. 3/3 EUR spec met.
