# RBI Repo Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** RBI Repo Rate (~6x/year, 04:30 UTC / 10:00 IST)
**Status:** Live - via `predict-rbi.yml`

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED IRSTCI01INM156N (OECD Immediate <24h IN) | 1.00pp (deweighted, with 75bp scale-mismatch guard) |

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 14 INR.
