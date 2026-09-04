# CBRT Policy Rate Predictor - Model Card

**Model version:** `v2.1-wide-buckets`
**Event:** CBRT 1-Week Repo Rate (~12x/year monthly, 11:00 UTC / 14:00 TRT)
**Status:** Live via `predict-cbrt.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED INTDSRTRM193N (LIVE, matches CBRT ~38%) | 0.30pp |

Rule 32 pattern: TR keeps INTDSR alive (like CN, BR). Very-high-inflation
EMs seem to maintain this series.

**v2.1 wide-bucket upgrade (Rule 36 fix):** 100bp buckets replace
standard 25bp grid. CBRT typically moves 100-250bp per meeting
(post-2023); distribution now properly represents cut200/hike100
outcomes with meaningful probabilities. Bucket outcomes:
hike200/hike100/hold/cut100/cut200/cut300_plus.

## Change log

- **v2.1-wide-buckets (2026-09-05)** - upgraded to 100bp bucket grid
  to match CBRT's typical move size (Rule 36 fix).
- **v2-outcome-distribution (2026-09-04)** - first ship. Phase 17 TRY.
