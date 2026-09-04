# BCB Selic Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** BCB Selic Target Rate (~8x/year Copom, 21:30 UTC / 18:30 BRT)
**Status:** Live - via `predict-bcb.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED INTDSRBRM193N (LIVE, matches Selic target ~21%) | 0.30pp |

Rule 32: BR keeps INTDSRBRM193N live (like CN). This is the scale-correct
anchor for Selic; IRSTCI01BRM156N (14.4%) is interbank overnight, not policy.

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 15 BRL.
