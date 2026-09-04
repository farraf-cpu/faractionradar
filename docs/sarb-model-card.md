# SARB Repo Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** SARB Repo Rate (~6x/year MPC, 13:00 UTC / 15:00 SAST)
**Status:** Live via `predict-sarb.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED IRSTCI01ZAM156N (LIVE, matches SARB ~7%) | 0.15pp |

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 16 ZAR.
