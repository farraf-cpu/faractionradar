# KR CPI Predictor - Model Card

**Model version:** `v1.1-kosis`
**Event:** KR CPI y/y (monthly, ~2nd of following month, 08:00 KST, KOSIS)
**Status:** Live via `predict-krcpi.yml`

## What v1.1-kosis does

Inverse-MAE-weighted point estimate over up to 2 sub-models.

Sub-models:
| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "CPI y/y" KRW | ~0.15 |
| KOSIS 3-mo mean trend | `kosis.kr/openapi` (orgId 101, tblId DT_1J17001, itmId T20, objL1 A) | ~0.25 |

**Consensus-only fallback:** if `KOSIS_APP_ID` env var is unset (or
key invalid), predictor falls back to consensus-only (equivalent to
v1). No hard errors — trend sub-model soft-skips.

## Activation

1. Register at **https://kosis.kr/openapi/index/index.jsp** (free).
2. Add resulting `apiKey` as GitHub Actions secret `KOSIS_APP_ID` on
   `farraf-cpu/faractionradar`.
3. Next scheduled cron will fetch KOSIS trend automatically.

## Why KOSIS is required

- FRED `CPALTT01KRM659N` dead since 2023-11.
- KOSIS is Statistics Korea's authoritative portal and the only free
  fresh source of monthly KR CPI data.

Follows Rule 39 pattern (native CB API integration) established by
jpcpi v1.1-estat (Phase 27).

## Change log

- **v1.1-kosis (2026-09-05)** - added KOSIS trend anchor sub-model
  (opt-in via KOSIS_APP_ID). Bumped from consensus-only v1.
- **v1-simple-blend (2026-09-04)** - first ship. Phase 12 KRW.
