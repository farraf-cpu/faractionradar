# Phase 8 learnings — CH trio (SNB + Swiss CPI + Swiss GDP)

Phase 8 opened 2026-09-04 (same-day after Phase 7, ~30min).
Country coverage: **8 majors** (USD/EUR/GBP/JPY/AUD/CAD/NZD/CHF).

## What's live now (Phase 8 additions)

**CHF expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| snb | SNB Policy Rate (quarterly MPA) | v2-outcome-distribution: consensus + IR3TIB01CHM156N SARON-adjacent anchor (inflated MAE) | 18:30 + 01:30 T-0 |
| chcpi | Swiss CPI y/y (monthly) | v1-simple-blend consensus-only (CPALTT01CHM659N stale) | 18:35 + 22:00 T-0 |
| chgdp | Swiss GDP q/q | v1-simple-blend: consensus + CLVMNACSCAB1GQCH 4-qtr trend | 18:40 + 22:30 T-0 |

**Worker changes:**
- 67 total predictors (was 64)
- CHF branch in `predictionSlugFor`
- Hardcoded SNB_MEETINGS/CHCPI/CHGDP arrays

## Rules learned (reinforced)

### Rule 31: CH has better FRED coverage than NZ (esp for GDP)

Comparing small-country FRED coverage:
- NZ: 1 usable series (IR3TIB01NZM156N only; CPI + GDP absent/dead)
- CH: 3 usable series (IR3TIB01CHM156N + CPALTT01CHM659N stale + CLVMNACSCAB1GQCH live GDP)

Reason: OECD's chained real GDP series (CLVMNACSCAB1GQCH suffix) has
coverage for CH but not NZ. This means CH chgdp gets a real trend
anchor while NZ nzgdp is consensus-only.

**How to apply:** For each new small country, test the OECD chained
real GDP series pattern (`CLVMNACSCAB1GQ{CTY}`) before assuming
consensus-only. Also `CPALTT01{CTY}Q659N` (quarterly CPI y/y) and
`CPALTT01{CTY}M659N` (monthly CPI y/y). Recent data availability
varies country-by-country.

## What's outstanding (post-Phase 8)

**Phase 8.1 candidates:**
- BFS Statistical Portal API for Swiss CPI live trend
- SARON futures curve for SNB direct market path

**Phase 9 candidates:**
- Nordic (SE/NO): SEK/NOK currencies, Riksbank + Norges Bank
- Emerging (KR/MX/SG/ZA): larger effort, thin data
- CN: PBOC + China CPI + China GDP (biggest EM but data quality
  questions)

**True Bayesian** — still blocked.

## Progression timeline (all same-day 2026-09-04)

- Phase 2 (EUR) 4-6h → Phase 3 (UK) 1h → Phase 4 (JP) 45m →
  Phase 5 (AU) 40m → Phase 6 (CA) 30m → Phase 7 (NZ) 30m →
  Phase 8 (CH) 30m

7 country expansions in one session. 21 new predictors + 7 country
branches + 21 hardcoded meeting date arrays.

## Ledger of Phase 8 commits

Session start (Phase 7 wrap): bbf3af1

Phase 8 predictor-repo commits:
- e91ed5d — Phase 8 CH trio: emit_snb/chcpi/chgdp + should_run +
  workflows + model cards + smoke reports

Worker-side companion commit:
- e0a2873 — calendar-worker: Phase 8 CHF branch (deployed as wrangler
  version dc8bd837-9c7d-42d6-b4b5-496dade1cf50)

## Phase 8 completion status

**Rook-side shippable items: 100% complete.**

Country coverage: 8 (USD/EUR/GBP/JPY/AUD/CAD/NZD/CHF). Total predictors: 67.
