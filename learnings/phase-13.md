# Phase 13 learnings — MX trio (Banxico + MX CPI + MX GDP)

Phase 13 opened 2026-09-05 (first cross-day session extension).
Country coverage: **13 areas**.

## What's live now (Phase 13 additions)

**MXN expansion — 3 predictors:**

| Slug | Event | Approach |
|------|-------|----------|
| banxico | Banxico Overnight Rate (~8x/year) | v2-outcome-distribution with 75bp scale-mismatch guard |
| mxcpi | MX CPI y/y (monthly) | v1-simple-blend consensus-only |
| mxgdp | MX GDP q/q (quarterly) | v1-simple-blend consensus-only |

**Worker: 82 total predictors (was 79).**

## Rules learned

### Rule 35: Not all "live" OECD Immediate Rates are scale-correct

MX FRED `IRSTCI01MXM156N` returns "live" (2026-06 obs at 5.19%) but is
100-200bp BELOW the actual Banxico Overnight Target (~7-11% range).
Using it as anchor caused Banxico smoke to false-positive hike50 at
100% probability, cascading from the outcome-distribution being
grid-centered on a wrong-scale anchor.

**Fix pattern (encoded in emit_banxico.py):** Auto-drop anchor when
|consensus - anchor| > 75bp. Fall back to consensus-centered outcome
distribution (`compute_outcome_distribution(point, sigma, consensus)`
instead of `... anchor`).

**How to apply:** Before shipping a new country's v2 rate predictor,
smoke-test with realistic consensus. If lean shows > +100bp move
because anchor is way off from consensus, add the 75bp guard OR
switch to consensus-only. This is a *runtime* guard — safer than
static MAE inflation because it responds to per-event mismatches
rather than trusting a single MAE estimate.

**Related to Rules 30/33:** Rule 30 = MAE weighting for imperfect
anchors (SE, NZ, CH cases). Rule 33 = prefer scale-correct-stale
over fresh-wrong-scale (CN case). Rule 35 = when even the
scale-correct fallback is missing, use a runtime guard.

## Country coverage — 13 CURRENCY AREAS

USD 46, EUR 3, GBP 3, JPY 3, AUD 3, CAD 3, NZD 3, CHF 3, SEK 3, CNY 3,
NOK 3, KRW 3, MXN 3 = **82 predictors**

## Ledger of Phase 13 commits

Predictor: ceafd9d (Phase 13 MX trio).
Worker: 6a3cfcb (deployed as 00e7c545-c2fb-4be1-ba27-fcfc08727263).

## Phase 14+ candidates

- IN (India): RBI + India CPI + India GDP
- BR (Brazil): BCB Selic + Brazil CPI + Brazil GDP
- ZA (South Africa): SARB
- SG/TW/HK Asian financial centers
