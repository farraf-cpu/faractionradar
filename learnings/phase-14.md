# Phase 14 learnings — IN trio (RBI + IN CPI + IN GDP)

Phase 14 opened 2026-09-05. Country coverage: **14 areas**.

## What's live now

**INR — 3 predictors:**
- rbi: v2-outcome-distribution + IRSTCI01INM156N anchor + 75bp guard
- incpi: v1-simple-blend consensus-only
- ingdp: v1-simple-blend consensus-only

**Worker: 85 total predictors (was 82).**

## Rules learned

None new — pattern held. IRSTCI01INM156N was live (5.5%) and close to
RBI repo rate scale. 75bp guard would kick in if consensus diverges.

## Country coverage — 14 CURRENCY AREAS: 85 predictors

USD 46, EUR 3, GBP 3, JPY 3, AUD 3, CAD 3, NZD 3, CHF 3, SEK 3, CNY 3,
NOK 3, KRW 3, MXN 3, INR 3

## Ledger

Predictor: 48fdcb4. Worker: 70baa77 (deployed as 0517ac9d).

## Phase 15+ candidates

- BR (Brazil), ZA (South Africa), TR (Turkey)
- SG/TW/HK (Asian financial centers)
