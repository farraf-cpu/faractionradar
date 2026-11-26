# ADP Non-Farm Employment prediction — target 2026-12-02 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-26T15:15:21.963771+00:00

## Final pick

**+69K** private payroll change (SA)

- 68% CI: [+29K, +109K] · sigma source: prior (inverse-MAE)
- 95% CI: [-11K, +149K]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 30K |
| trend | +69K | 40K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~30K MAE) + FRED
ADPMNUSNERSA 3-month trend (~40K MAE). Short trend window because ADP
series has been noisier since the 2022 methodology overhaul.

## What ADP does + doesn't predict

ADP historically correlates ~0.5-0.7 with NFP first-print. Post-2022
methodology change (ADP now uses cell-phone geolocation + payroll data
instead of just payroll data), correlation is looser. It's a leading
indicator but NOT a NFP proxy — reader shouldn't extrapolate directly.

Our NFP predictor's v1-bayesian-blend already uses ADP as a sub-model input,
so this ADP-standalone predictor gives readers visibility into the "ADP
component" of NFP's ensemble before NFP itself fires on Friday.

Phase 2 target: NFP-first-print correlation-adjusted sub-model that
translates the ADP surprise into an expected NFP delta.
