# KR CPI Predictor - Model Card

**Model version:** `v1-simple-blend`
**Event:** KR CPI y/y (monthly, ~2nd of following month, 00:00 UTC / 09:00 KST, KOSIS)
**Status:** Live - via `predict-krcpi.yml`

Consensus-only. FRED `CPALTT01KRM659N` dead since 2023-11.

Sub-models: FF consensus (~0.15pp MAE).

- **v1-simple-blend (2026-09-04)** - first ship. Phase 12 KRW expansion.
