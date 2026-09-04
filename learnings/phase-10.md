# Phase 10 learnings — CN trio (PBOC + CN CPI + CN GDP)

Phase 10 opened 2026-09-04. Country coverage: **10 majors + BRIC entry**
(USD/EUR/GBP/JPY/AUD/CAD/NZD/CHF/SEK/CNY).

## What's live now (Phase 10 additions)

**CNY expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| pboc | PBOC 1Y LPR (monthly) | v2-outcome-distribution: consensus + INTDSRCNM193N anchor | 18:30 + 01:30 T-0 |
| cncpi | CN CPI y/y (monthly) | v1-simple-blend consensus-only | 18:35 + 22:00 T-0 |
| cngdp | CN GDP y/y (quarterly) | v1-simple-blend consensus-only (both FRED GDP series dead/missing) | 18:40 + 22:30 T-0 |

**Worker: 73 total predictors (was 70).**

## Rules learned

### Rule 32: Rule 27's Discount-Rate-Dead is NOT universal — CN is the exception

After 4 confirmations (UK/JP/AU/CA), I assumed all `INTDSR{CTY}M193N`
FRED series were dead. Wrong: **China's `INTDSRCNM193N` is live**
(2025-06 obs at 2.9%), tracking PBOC Discount Rate with ~15 month lag.

For CN this was the BETTER anchor choice than the fresher-but-wrong-
scale `IR3TIB01CNM156N` (SHIBOR 3-mo at 1.51%, ~160bp below actual
1Y LPR). SHIBOR is a interbank rate, LPR is a policy/lending rate —
different tenors entirely.

**How to apply:** Always check `INTDSR{CTY}M193N` liveness AS WELL as
`IRSTCI01{CTY}M156N` when scouting anchors for a new country. Don't
assume dead based on prior patterns — verify per country.

### Rule 33: Rate scale mismatch is worse than staleness

When picking between two imperfect anchors:
- SHIBOR 3-mo: fresh (1 month lag) but 160bp wrong scale (interbank vs policy)
- INTDSR Discount Rate: 15-month stale but within 20bp of policy rate

The stale-but-correct-scale wins. A 160bp scale mismatch cascades
directly into outcome-distribution false positives (initial PBOC
smoke gave hike50 100% probability because consensus was 160bp above
anchor). A 20bp staleness only shifts distribution modestly.

**How to apply:** Rank anchor candidates by ABS(anchor - typical_consensus).
Take the smallest gap, not the freshest. If both are wrong-scale,
consensus-only is safer than either.

## Country coverage — 10 MAJORS DONE

USD 46, EUR 3, GBP 3, JPY 3, AUD 3, CAD 3, NZD 3, CHF 3, SEK 3, CNY 3
= **73 total predictors across 10 currency areas** (all G7 + G10
majors + China).

## Progression timeline (all same-day 2026-09-04)

Phase 2 (EUR) 4-6h → Phase 3 (UK) 1h → Phase 4 (JP) 45m → Phase 5 (AU) 40m →
Phase 6 (CA) 30m → Phase 7 (NZ) 30m → Phase 8 (CH) 30m → Phase 9 (SE) 30m →
Phase 10 (CN) 30m.

**9 country expansions in one session. 27 new predictors, 9 country branches.**

## Phase 11 candidates

- NO: Norges Bank + Norway CPI + Norway GDP (Nordic pair completion)
- KR: BOK + Korea CPI + Korea GDP
- MX: Banxico + Mexico CPI + Mexico GDP
- IN: RBI + India CPI + India GDP (thin FRED data expected)

## Ledger of Phase 10 commits

Session start (Phase 9 wrap): b9f2990

Phase 10 predictor-repo commits:
- cd7a2b6 — Phase 10 CN trio

Worker-side commit:
- 35c0650 — calendar-worker: Phase 10 CNY branch (deployed as
  1c4efa6f-b0e4-4300-ad35-63a87e71761a)

## Phase 10 completion status

**Rook-side shippable items: 100% complete.**
