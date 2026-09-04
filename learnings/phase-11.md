# Phase 11 learnings — NO trio (Norges Bank + NO CPI + NO GDP)

Phase 11 opened 2026-09-04. Nordic pair now complete (SE + NO).
Country coverage: **11 areas** (10 majors + China).

## What's live now (Phase 11 additions)

**NOK expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| norges | Norges Bank Policy Rate | v2-outcome-distribution: consensus + IRSTCI01NOM156N LIVE anchor (NORMAL MAE 0.15pp) | 18:30 + 01:30 T-0 |
| nocpi | NO CPI y/y (monthly) | v1-simple-blend consensus-only | 18:35 + 22:00 T-0 |
| nogdp | NO GDP q/q (quarterly) | v1-simple-blend: consensus + CLVMNACSCAB1GQNO 4-qtr trend | 18:40 + 22:30 T-0 |

**Worker: 76 total predictors (was 73).**

## Rules learned (reinforced)

### Rule 34: OECD IRSTCI01 series is NOT uniformly stale — freshness varies wildly by country

Comparing OECD Immediate <24h series across all Phase-4+ countries:
- IRSTCI01JPM156N (JP): LIVE, 2026-06 ✓
- IRSTCI01AUM156N (AU): LIVE, 2026-06 ✓
- IRSTCI01CAM156N (CA): LIVE, 2026-06 ✓
- **IRSTCI01NOM156N (NO): LIVE, 2026-06** ✓
- IRSTCI01SEM156N (SE): stale 2020-10 ✗ (6 years)
- IRSTCI01CHM156N (CH): stale 2024-03 ✗ (30 months)
- IRSTCI01NZM156N (NZ): stale 2024-12 ✗ (21 months)
- IRSTCI01CNM156N (CN): stale 2025-06 ✗ (15 months)

**Pattern:** Fresh for JP/AU/CA/NO (all G10 + core Nordic). Stale for
SE (surprisingly), CH, NZ, CN. Not obviously correlated with country
size, currency importance, or geographic region.

**How to apply:** Always verify IRSTCI freshness per country before
declaring the recipe safe. When stale, fall back to `IR3TIB01{CTY}M156N`
with inflated MAE 0.30pp (Rule 30 pattern). When both stale, consensus-only.

## Country coverage — 11 CURRENCY AREAS

USD 46, EUR 3, GBP 3, JPY 3, AUD 3, CAD 3, NZD 3, CHF 3, SEK 3, CNY 3, NOK 3
= **76 predictors**

**All G7 + all G10 + China covered.** Nordic pair complete.

## Progression timeline (all same-day 2026-09-04)

Phase 2 (EUR) 4-6h → 3 (UK) 1h → 4 (JP) 45m → 5 (AU) 40m → 6 (CA) 30m →
7 (NZ) 30m → 8 (CH) 30m → 9 (SE) 30m → 10 (CN) 30m → 11 (NO) 30m.

**10 country expansions in one session. 30 new predictors, 10 country branches.**

## Ledger of Phase 11 commits

Session start (Phase 10 wrap): 9ea433f

Phase 11 predictor-repo commits:
- fad7103 — Phase 11 NO trio

Worker-side commit:
- c8a8994 — calendar-worker: Phase 11 NOK branch (deployed as
  2723bddc-b67c-4e3a-a102-1fb0a4e28b44)

## Phase 11 completion status

**Rook-side shippable items: 100% complete.** All G10 done.

## Phase 12+ candidates

- KR (Korea), MX (Mexico), IN (India) — emerging majors
- SG (Singapore), TW (Taiwan), HK (Hong Kong) — Asian financial centers
- Consolidation phase: real-Bayesian calibration when resolutions accumulate
