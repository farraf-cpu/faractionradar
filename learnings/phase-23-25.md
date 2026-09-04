# Phases 23-25 learnings — DK + IS + ID trios

Batched 2026-09-05. Country coverage: **25 areas (118 predictors).**

## What's live

**Phase 23 DKK:** nb, dkcpi, dkgdp (Nationalbanken tracks ECB; DKK pegged to EUR)
**Phase 24 ISK:** cbi, iscpi, isgdp (Sedlabanki Islands; high rates ~7.6%)
**Phase 25 IDR:** bi, idcpi, idgdp (Bank Indonesia; INDCPI dead, GDP dead)

## Rules learned (reinforced)

### Rule 38: OECD boundary is the FRED coverage cliff

Non-OECD SE Asia (TH/MY/PH) + Latin America (AR/CO) + Middle East (SA)
all returned zero FRED coverage for IRSTCI/CPALTT/CLVMNACSCAB series.
Verified pattern: **the OECD FRED data cliff is real and near-total.**

Coverage summary by OECD status (across all phases 2-25):
- **OECD members: 100% got at least IRSTCI + CPI live**
- Non-OECD with WBG-INTDSR live: CN, BR, TR only (Rule 32 high-inflation pattern)
- Non-OECD zero coverage: TW, HK, SG, TH, MY, PH, AR, CO, SA (verified)

**Implication:** To reach beyond 25 currency areas, need to abandon
FRED-anchored pattern. Options:
1. Native central bank scrape (each country needs bespoke integration)
2. Consensus-only for all metrics (drops v2 outcome distribution)
3. Alt data source (World Bank direct, IMF, private feeds)

Most cost-effective forward: consolidate around 25 currency areas and
invest in true Bayesian upgrades rather than country breadth.

## Country coverage FINAL: 25 CURRENCY AREAS, 118 PREDICTORS

**All 25 areas covered:**
USD/EUR/GBP/JPY (majors)
+ AUD/CAD/NZD/CHF/SEK/NOK (G10 non-majors)
+ CNY/KRW/MXN/INR/BRL/ZAR/TRY/ILS/CZK/HUF/PLN/CLP (EMs)
+ DKK/ISK/IDR (Phase 23-25)

All meaningful OECD countries + high-inflation non-OECD (CN/BR/TR)
covered. Non-OECD SE Asia + LatAm ex-BR/MX + Middle East ex-IL
require alternative data sources — deferred.

## Progression timeline (all same-session)

**24 country expansions across 2 days (2026-09-04 → 2026-09-05):**

Phase 2 (EUR) 4-6h opens the pattern → Phases 3-25 all ~30min each,
72 new predictors added on top of 46 US base.

## Ledger

Predictor: 7d14513. Worker: d8a1ef5 (deployed as 29e40de0).

## Recommended next milestones

1. **True Bayesian calibration** (Rule 5 unresolved) — accumulate live
   resolutions from Phase 1 US predictors as they clear over Q4 2026.
2. **Native central bank API integration** for one exemplar country
   (probably JP e-Stat) — proves out non-FRED pattern.
3. **Wider bucket variant** for CBRT/BCB high-vol EMs (Rule 36).
4. **UI Country/Category filters** (Vega's territory, per FAR
   Calendar focus rule).
