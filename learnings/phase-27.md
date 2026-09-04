# Phase 27 learnings — jpcpi v1 → v1.1-estat (native API integration)

Phase 27 opened 2026-09-05. First non-FRED native central-bank API
integration. Country count unchanged at 25.

## What changed

**jpcpi v1 → v1.1-estat**: Added e-Stat trend anchor sub-model.
- Endpoint: `api.e-stat.go.jp/rest/3.0/app/json/getStatsData`
- Series: `statsDataId=0003143513, cdCat01=0001, cdCat02=01`
  (Monthly CPI, National Core, y/y % change)
- Auth: free `appId` registered at https://www.e-stat.go.jp/api/en/
- Env: `ESTAT_APP_ID` GHA secret
- Behavior: soft-skips when key missing OR API errors → falls back
  to v1 consensus-only.

## Rule 39: Native CB API integration pattern

First non-FRED external data source integrated. Established pattern
for future upgrades:

1. **Opt-in via env var** — `{SOURCE}_APP_ID` or `{SOURCE}_API_KEY`.
   Predictor ships live regardless of whether key is set.
2. **Soft-skip on failure** — API errors, missing key, missing values
   all degrade to consensus-only. No hard-fail (Rule 8 principle).
3. **Free tier only** — always use no-cost registrations. Users
   should be able to activate without spending money.
4. **Document activation in model card** — step-by-step registration
   + secret-add instructions. New users must be able to activate
   without prior context.
5. **MODEL_VERSION suffix** — name the version after the data source
   (`v1.1-estat`, `v1.1-ons`, `v1.1-statscan`) so users know which
   sub-model provides the anchor.

## Why FRED alternatives fail for JP CPI

- FRED: `JPNCPIALLMINMEI`, `CPALTT01JPM659N`, `JPNCPICORMINMEI` all
  return empty values since 2022-04.
- OECD SDMX direct: returns Japan CPI data but STOPS at 2021-06.
- IMF DataMapper: annual only, no monthly.
- World Bank API: annual only, no monthly.
- BIS SDMX: schema errors on all queries tried.
- BOJ website: HTML, no JSON API endpoint.

**e-Stat is the only free source of fresh monthly JP CPI data.**

## Pattern for other countries with dead FRED CPI

Following the same v1.1-native template, upgrades queued for:
- **jpcpi** ✅ shipped
- **krcpi** → KOSIS API (needs `KOSIS_API_KEY`)
- **incpi** → MoSPI (registration required)
- **cncpi** → NBS national data (public, no auth)
- **brcpi** → IBGE SIDRA API (public, no auth)
- **mxcpi** → INEGI API (needs `INEGI_TOKEN`)
- **cacpi** → StatCan WDS API (public, no auth)
- **ukcpi** → ONS API (public, no auth)
- **secpi/nocpi/dkcpi/iscpi** → SCB/SSB/DST/Hagstofa APIs
- **hucpi/plcpi/czcpi** → KSH/GUS/CZSO APIs
- **ilcpi/aucpi/nzcpi** → CBS/ABS/StatsNZ APIs

Priority order: JP (done) → KR → IN → CN → BR (Latin America top-tier).
Estimated ~1h per country, mostly finding the right statsDataId / API
endpoint per each national statistics service.

## Ledger

Predictor: 9105bc0. Worker: swept into Vega's 1ed9804 (auto-sweep
pattern per memory). Deploy: 48261c43-5784-4f57-9379-9e08d6f5d185.

## Country + quality summary post-Phase 27

- 25 currency areas (unchanged)
- 118 predictors (unchanged)
- 3 v1.1/v2.1 upgrades: CBRT+BCB wide-buckets (Phase 26), jpcpi
  e-Stat (Phase 27)
- 39 unique rules
- 25 non-USD country expansions + 2 quality-upgrade phases in 2 days
