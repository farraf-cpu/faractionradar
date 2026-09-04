# JP CPI Predictor - Model Card

**Model version:** `v1.1-estat`
**Event:** JP National Core CPI y/y (~19th-27th of following month, 08:30 JST / 23:30 UTC prior day)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-jpcpi.yml`

## What v1.1-estat does

Inverse-MAE-weighted point estimate over up to 2 sub-models.

Sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from worker `?read` for "National Core CPI y/y" JPY | ~0.15 |
| e-Stat 3-mo mean trend | `api.e-stat.go.jp` National Core CPI y/y series (statsDataId `0003143513`, cdCat01 `0001`) | ~0.25 |

**Consensus-only fallback:** if `ESTAT_APP_ID` env var is unset (or
key is invalid), predictor falls back to consensus-only behavior
(equivalent to v1). No hard errors — soft skip on trend sub-model.

## Activation

1. Register at **https://www.e-stat.go.jp/api/en/** (free, email
   confirmation, ~5 minutes).
2. Add the resulting `appId` as GitHub Actions secret named
   `ESTAT_APP_ID` on `farraf-cpu/faractionradar`.
3. Next scheduled cron will fetch e-Stat trend automatically.

Local test:
```bash
ESTAT_APP_ID="your-key" JPCPI_CONSENSUS="2.7" \
  JPCPI_RELEASE_DATE="2026-09-19" JPCPI_DAYS_OUT="15" \
  UPLOAD_AUTH_KEY="dummy" CALENDAR_WORKER_URL="https://httpbin.org/anything" \
  python emit_jpcpi.py
```

## Why e-Stat is required

FRED's Japan CPI series are all discontinued as of 2022:
- `JPNCPIALLMINMEI`, `CPALTT01JPM659N`, `JPNCPICORMINMEI` — all
  return empty observations.
- OECD.Stat direct API also returns pre-2022 data only for JP.
- IMF/World Bank publish annual only, not monthly.

e-Stat is Japan's authoritative statistics portal and the only free
source of monthly National Core CPI y/y data. API is public but
requires free registration for rate-limiting purposes.

## Change log

- **v1.1-estat (2026-09-05)** - added e-Stat trend anchor sub-model
  (opt-in via ESTAT_APP_ID secret). Bumped from consensus-only v1.
- **v1-simple-blend (2026-09-04)** - first ship. Phase 4 JPY
  expansion, consensus-only pending e-Stat integration.
