# Phase 18 learnings — IL trio (BoI + IL CPI + IL GDP)

Phase 18 opened 2026-09-05. Country coverage: **18 areas**.

## What's live now

**ILS — 3 predictors:**
- boi: v2 + IRSTCI01ILM156N anchor (LIVE 3.75%)
- ilcpi: v1 consensus-only
- ilgdp: v1 consensus-only

**Worker: 97 total predictors.**

## Rules learned

### Rule 37: OECD-membership predicts FRED coverage more than country size/importance

Discovered when TW/HK/SG all returned zero coverage for IRSTCI/CPALTT/CLVMNACSCAB series. These are among the world's most important financial centers but are NOT OECD members. The IRSTCI01<CTY>M156N and CPALTT01<CTY>M659N series are OECD-published, so non-OECD economies simply aren't in FRED via that path.

**Coverage by OECD membership (verified this session):**
- OECD members with live FRED: US, JP, GB, EU, AU, CA, NZ, CH, SE, KR, MX, NO, IL, CZ, HU, PL, CL
- OECD members with stale FRED: (some Eastern EU only stale, not dead)
- Non-OECD without FRED: TW, HK, SG, CO, and likely CN (kept via WBG), BR (WBG), TR (WBG), ZA (WBG)
- Non-OECD with live INTDSR (WBG): CN, BR, TR (Rule 32 high-inflation pattern)

**How to apply:** Before assuming FRED coverage for a new country, check OECD membership. If non-OECD, expect only sparse coverage (maybe WBG-INTDSR only). Fallback strategies: (a) consensus-only pattern (like deifo), (b) native central bank scrape, (c) skip country entirely.

## Country coverage — 18 CURRENCY AREAS: 97 predictors

## Phase 19+ candidates

- CZ (Czech), HU (Hungary), PL (Poland) — CE3 with LIVE FRED
- CL (Chile) — LIVE FRED IRSTCI 4.5%
- Consolidation: TW/HK/SG would need consensus-only pattern OR skip
