# Phase 21 learnings — PL trio (CE3 complete)

Phase 21 opened 2026-09-05. Country coverage: **21 areas**.
**CE3 (Central Europe) complete: CZ + HU + PL.**

## What's live now

**PLN — 3 predictors:**
- nbp: v2 + IRSTCI01PLM156N with 75bp scale-mismatch guard (POLONIA overnight vs Reference Rate)
- plcpi: v1 consensus-only
- plgdp: v1 + FRED CLVMNACSCAB1GQPL trend

**Worker: 106 total predictors.**

## Rules learned

**Rule 35 fires more broadly than expected.** Initially discovered on
Banxico (MX, ~150bp gap). Now also fires on NBP (PL, ~150bp gap).
Two cases in two EMs where the OECD IRSTCI series reports an
overnight/interbank rate rather than the central bank policy rate.

**Guard now included by default in all new EM rate predictors going
forward.** Should probably retrofit to older EM predictors that were
copied before the guard existed (KR/ZA/IL/CZ/HU — check if they
would benefit).

## Country coverage — 21 CURRENCY AREAS: 106 predictors

## Phase 22+ candidates

- CL (Chile) — LATAM continuation
- ID/TH/MY/PH — SE Asia
