# BR CPI (IPCA) Predictor - Model Card

**Model version:** `v1.1-sidra`
**Event:** BR IPCA y/y (monthly, ~9-11th of following month, 12:00 UTC / 09:00 BRT, IBGE)
**Status:** Live via `predict-brcpi.yml`

## What v1.1-sidra does

Inverse-MAE-weighted blend of 2 sub-models. **No API key required —
SIDRA is a public unauthenticated endpoint.**

Sub-models:
| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" BRL | ~0.15 |
| SIDRA IPCA 12-mo y/y 3-mo mean | `apisidra.ibge.gov.br` table 1737, variable 2265 | ~0.20 |

**Fully automatic — no secret to add.** Trend soft-skips gracefully
if SIDRA is unreachable (network issue); predictor still ships
consensus-only in that case.

## Why SIDRA is different from Rule 39 keyed-API pattern

Most national statistics APIs (e-Stat/KOSIS/MoSPI/StatCan/ONS) require
free registration for API keys. IBGE SIDRA is the exception — Brazil
publishes it as fully public data with no auth. No env var setup
needed on `farraf-cpu/faractionradar`; predictor activates the trend
sub-model automatically.

## Change log

- **v1.1-sidra (2026-09-05)** - added SIDRA trend anchor sub-model
  (activates automatically, no key required). First fully-automatic
  native-API integration under Rule 39.
- **v1-simple-blend (2026-09-04)** - first ship. Phase 15 BRL.
