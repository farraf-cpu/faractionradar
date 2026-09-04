# CBRT Policy Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** CBRT 1-Week Repo Rate (~12x/year monthly, 11:00 UTC / 14:00 TRT)
**Status:** Live via `predict-cbrt.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED INTDSRTRM193N (LIVE, matches CBRT ~38%) | 0.30pp |

Rule 32 pattern: TR keeps INTDSR alive (like CN, BR). Very-high-inflation
EMs seem to maintain this series.

**Caveat:** CBRT rate moves are often 100-250bp (not 25bp). The 25bp
bucket distribution understates cut/hike magnitudes. Users should
weight the point estimate over the outcome buckets.

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 17 TRY.
