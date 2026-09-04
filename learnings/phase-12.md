# Phase 12 learnings — KR trio (BOK + KR CPI + KR GDP)

Phase 12 opened 2026-09-04. First emerging-market entry (Korea, though
still a developed economy by most measures).

## What's live now (Phase 12 additions)

**KRW expansion — 3 predictors:**

| Slug | Event | Approach |
|------|-------|----------|
| bok | BOK Base Rate (~8x/year) | v2-outcome-distribution: consensus + IRSTCI01KRM156N LIVE anchor |
| krcpi | KR CPI y/y | v1-simple-blend consensus-only |
| krgdp | KR GDP q/q Advance | v1-simple-blend consensus-only (30-day fastest globally) |

**Worker: 79 total predictors (was 76).**

## Rules learned

None new — pattern held. IRSTCI01KRM156N was live (like JP/AU/CA/NO
pattern from Rule 34), CPI + GDP series dead (typical for non-Western).

## Country coverage — 12 CURRENCY AREAS

USD 46, EUR 3, GBP 3, JPY 3, AUD 3, CAD 3, NZD 3, CHF 3, SEK 3, CNY 3,
NOK 3, KRW 3 = **79 predictors**

**Emerging-market expansion begins with Korea (still ~developed).**

## Ledger of Phase 12 commits

Phase 12 predictor-repo commits: 7293619 (main + rebase to ea15a17).
Worker-side commit: 34adecb (deployed as 60bb9993).

## Phase 12 completion status

**Rook-side shippable items: 100% complete.**

## Progression timeline

Phase 2 (EUR) 4-6h → 3 (UK) 1h → 4-12 all ~30m each.
**11 country expansions in one session. 33 new predictors, 11 country branches.**

## Phase 13+ candidates

- MX (Mexico): Banxico + Mexico CPI + Mexico GDP
- IN (India): RBI + India CPI + India GDP
- ZA (South Africa): SARB
- SG/TW/HK: Asian financial centers
- BR (Brazil): BCB
