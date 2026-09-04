# BCB Selic Predictor - Model Card

**Model version:** `v2.1-wide-buckets`
**Event:** BCB Selic Target Rate (~8x/year Copom, 21:30 UTC / 18:30 BRT)
**Status:** Live via `predict-bcb.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED INTDSRBRM193N (LIVE, matches Selic target ~21%) | 0.30pp |

Rule 32: BR keeps INTDSRBRM193N live (like CN). Scale-correct anchor
for Selic; IRSTCI01BRM156N (14.4%) is interbank overnight, not policy.

**v2.1 wide-bucket upgrade (Rule 36 fix):** 50bp buckets replace
standard 25bp grid. Selic typically moves in 25-100bp increments
(larger than DM but tighter than CBRT). 50bp bucket resolution matches
BCB's realistic move sizes. Bucket outcomes: hike100/hike50/hold/
cut50/cut100/cut150_plus.

## Change log

- **v2.1-wide-buckets (2026-09-05)** - upgraded to 50bp bucket grid
  to match Selic's typical move size (Rule 36 fix, tuned per country).
- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 15 BRL.
