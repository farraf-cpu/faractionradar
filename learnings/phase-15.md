# Phase 15 learnings — BR trio (BCB + BR CPI + BR GDP)

Phase 15 opened 2026-09-05. Country coverage: **15 areas**.

## What's live now

**BRL — 3 predictors:**
- bcb: v2-outcome-distribution + INTDSRBRM193N anchor (LIVE, matches Selic ~21%)
- brcpi: v1-simple-blend consensus-only
- brgdp: v1-simple-blend consensus-only

**Worker: 88 total predictors (was 85).**

## Rules learned (reinforced)

**Rule 32 pattern reconfirmed:** Brazil, like China, keeps
`INTDSRBRM193N` LIVE and scale-correct. IRSTCI01BRM156N reports 14%
(interbank overnight) vs actual Selic ~21% — 700bp gap, unusable as
anchor. Always check both series and pick the scale-correct one.

Countries where INTDSR is LIVE (so far): CN, BR.
Countries where INTDSR is dead: UK, JP, AU, CA, NZ, CH, SE, NO, IN, MX.

Pattern hypothesis: high-inflation countries with elevated policy
rates may keep INTDSR current because it's actively tracked for
capital-flow risk. Low-inflation developed markets let it lapse.

## Country coverage — 15 CURRENCY AREAS: 88 predictors

USD 46, EUR 3, GBP 3, JPY 3, AUD 3, CAD 3, NZD 3, CHF 3, SEK 3, CNY 3,
NOK 3, KRW 3, MXN 3, INR 3, BRL 3

## Ledger

Predictor: 5519aa6. Worker: db63324 (deployed as a7f4e4a7).

## Phase 16+ candidates

- ZA (South Africa), TR (Turkey), TW (Taiwan), HK (Hong Kong), SG (Singapore)
