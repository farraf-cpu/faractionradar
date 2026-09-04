# Phase 9 learnings — SE trio (Riksbank + SE CPI + SE GDP)

Phase 9 opened 2026-09-04 (same-day after Phase 8, ~30min).
Country coverage: **9 majors** (USD/EUR/GBP/JPY/AUD/CAD/NZD/CHF/SEK).

## What's live now (Phase 9 additions)

**SEK expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| riksbank | Riksbank Policy Rate | v2-outcome-distribution: consensus + IR3TIB01SEM156N (STIBOR 3-mo) anchor (inflated MAE) | 18:30 + 01:30 T-0 |
| secpi | SE CPI y/y (monthly) | v1-simple-blend consensus-only (CPALTT01SEM659N stale) | 18:35 + 22:00 T-0 |
| segdp | SE GDP q/q | v1-simple-blend: consensus + CLVMNACSCAB1GQSE 4-qtr trend | 18:40 + 22:30 T-0 |

**Worker changes:**
- 70 total predictors (was 67)
- SEK branch in `predictionSlugFor`

## Rules learned (reinforced)

Same pattern as CH — Rule 30 (MAE weighting for imperfect anchors)
and Rule 31 (OECD chained real GDP works for SE too). No new
country-specific quirks caught.

## Progression timeline (all same-day 2026-09-04)

Phase 2 (EUR) 4-6h → Phase 3 (UK) 1h → Phase 4 (JP) 45m → Phase 5 (AU) 40m →
Phase 6 (CA) 30m → Phase 7 (NZ) 30m → Phase 8 (CH) 30m → Phase 9 (SE) 30m.

**8 country expansions in one session. 24 new predictors, 8 country branches,
24 hardcoded meeting date arrays.**

## What's outstanding (post-Phase 9)

**Phase 9.1 candidates:**
- STINA overnight index swap curve for Riksbank
- SCB Statistical Portal API for real CPI/GDP anchors

**Phase 10 candidates:**
- NO: Norges Bank + Norway CPI + Norway GDP (matches Nordic pair)
- CN: PBOC + China CPI + China GDP (biggest EM)
- KR / MX / SG / ZA: emerging majors

## Ledger of Phase 9 commits

Session start (Phase 8 wrap): 50a7cd9

Phase 9 predictor-repo commits:
- eebd943 — Phase 9 SE trio

Worker-side companion commit:
- 8445c3a — calendar-worker: Phase 9 SEK branch (deployed as version
  6db28cf2-4e73-4c44-a349-0ccc33191798)

## Phase 9 completion status

**Rook-side shippable items: 100% complete.**

Country coverage: 9 (USD/EUR/GBP/JPY/AUD/CAD/NZD/CHF/SEK). Total predictors: 70.
