# Banxico Overnight Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** Banxico Overnight Target Rate (~8x/year, 19:00 UTC winter / 13:00 CDMX)
**Status:** Live - via `predict-banxico.yml`

Consensus-only with scale-mismatch guard. FRED IRSTCI01MXM156N
(OECD Immediate <24h MX) reports ~5% but actual Banxico target is
~7-11% — 100-200bp scale mismatch. Predictor auto-drops anchor when
gap > 75bp, falls back to consensus-centered outcome distribution.

Sub-models:
| Sub-model | MAE |
|-----------|-----|
| FF consensus | 0.05pp |
| FRED IRSTCI01MXM156N | 1.00pp (usually dropped by scale-mismatch guard) |

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 13 MXN.
