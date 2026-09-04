# Phase 17 learnings — TR trio (CBRT + TR CPI + TR GDP)

Phase 17 opened 2026-09-05. Country coverage: **17 areas**.

## What's live now

**TRY — 3 predictors:**
- cbrt: v2 + INTDSRTRM193N anchor (LIVE 38.75% matches CBRT)
- trcpi: v1 consensus-only
- trgdp: v1 consensus-only

**Worker: 94 total predictors.**

## Rules learned (reinforced)

**Rule 32 hypothesis firmed up:** TR joins CN + BR keeping INTDSR live.
All three are high-inflation EMs. ZA is the counter-example (dead
INTDSR despite EM status). Updated hypothesis: **high-inflation
countries with elevated policy rates keep INTDSR active as an
FX-flow reference; low/moderate-inflation EMs let it lapse.**

## Rule 36: 25bp buckets are too narrow for high-vol EM rate predictors

CBRT typically moves in 100-250bp increments (not 25bp like DM
central banks). Standard outcome-distribution grid (hike50, hike25,
hold, cut25, cut50, cut75_plus with 25bp width) misrepresents these
moves — a 200bp cut ends up spread across cut50 + cut75_plus rather
than shown as its own outcome.

**How to apply:** For predictors where typical move size > 50bp,
either (a) widen buckets to match (100bp grid), (b) drop outcome
distribution and use point estimate only, or (c) note in model card
that point estimate is authoritative and buckets are illustrative.

Currently applied to CBRT via model card note. Same fix will be
needed for other high-vol EMs (ARG, VEN, etc if ever added).

## Country coverage — 17 CURRENCY AREAS: 94 predictors

## Phase 18+ candidates

- TW (Taiwan), HK (Hong Kong), SG (Singapore) — Asian financial centers
- Consolidation: true Bayesian, wider-bucket variant for high-vol EMs
