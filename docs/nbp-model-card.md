# NBP Reference Rate Predictor - Model Card

**Model version:** `v2-outcome-distribution`
**Event:** NBP Reference Rate (~12x/year monthly, 14:00 UTC / 15:00 CET)
**Status:** Live via `predict-nbp.yml`

Consensus + FRED IRSTCI01PLM156N with 75bp scale-mismatch guard
(the FRED series appears to report POLONIA overnight ~3.74% which
differs from NBP Reference Rate ~5.25%; guard fires when gap > 75bp).

- **v2-outcome-distribution (2026-09-05)** - first ship. Phase 21 PLN.
