# CNB Policy Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** CNB 2-week Repo Rate (~8x/year, 13:30 UTC / 14:30 CET)
**Status:** Live via `predict-cnb.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED IRSTCI01CZM156N (LIVE 3.58%) | 0.15pp |

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 19 CZK.
