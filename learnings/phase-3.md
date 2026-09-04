# Phase 3 learnings — UK trio (BOE + UK CPI + UK GDP)

Phase 3 opened 2026-09-04 (same-day ship after Phase 2 close, ~1h session).
Scope: 3 GBP predictors mirroring EUR trio pattern from Phase 2. Adds
GBP-branch routing to worker.

Read this before starting Phase 3.1 (adds JP or expands GBP core/services
splits). It builds on Phase 2 EUR expansion pattern.

## What's live now (Phase 3 additions)

**GBP expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| boe | BOE Bank Rate (MPC decision) | v2-outcome-distribution: consensus + FRED IUDSOIA (SONIA) anchor, discretized into 25bp bucket probabilities | 18:00 + 09:00 T-0 |
| ukcpi | UK CPI y/y | v1-simple-blend: consensus + FRED CPALTT01GBM659N 3-mo mean | 18:05 + 04:30 T-0 |
| ukgdp | UK Monthly GDP m/m | v1-simple-blend: consensus-only (ONS monthly GDP not on FRED cleanly) | 18:10 + 04:00 T-0 |

**Worker changes:**
- `predictionSlugFor` now routes by country: USD/EUR/**GBP** branches
- MODEL_REGISTRY: 49 → 52 entries (3 new)
- Hardcoded arrays: BOE_MEETINGS_2026/27, UKCPI_2026/27, UKGDP_2026/27
- Marquee pushes for boe/ukcpi/ukgdp/deifo (deifo was missing pre-Phase 3)

## Rules learned

### Rule 20: Verify FRED series liveness, not just existence

FRED `INTDSRGBM193N` (UK Discount Rate) returns HTTP 200 on
`https://fred.stlouisfed.org/series/<id>` but the underlying series is
**discontinued** — last observation dated 2013-03-01 at 0.5%. Using it
as a BoE Bank Rate anchor gave 0.5% instead of the actual ~3.75%.

**Bit us:** First BOE smoke test emitted 3.42% (skewed by 0.5% anchor)
and `+292bp move vs current rate` lean. Caught immediately in smoke.

**Fix:** Swapped to FRED `IUDSOIA` (Sterling Overnight Interbank
Average / SONIA). SONIA updates daily and tracks Bank Rate within
5-10bp. Returned 3.73% on smoke; BOE prediction landed at 3.75% "hold
expected" at 96% probability.

**How to apply:** Before wiring any FRED series as an anchor, query
the FRED API for the most recent observation and check the `date`
field. If it's more than 3 months old, the series is likely
discontinued — search for a live equivalent. HTTP-200 on `/series/<id>`
only means the metadata page exists, not that the data is current.

### Rule 21: Marquee push must accompany every new predictor prefix

Phase 2 shipped `deifo` and `eurcpi` predictors + their hardcoded
release-date arrays + should_run scripts, but forgot to push those
dates into the `items` array in `refreshUpcomingMarquee`. Result: their
gate scripts (`should_run_deifo.py`, `should_run_eurcpi.py`) never
found their events in `/public/upcoming-marquee` and would have
soft-skipped every day. Never caught because those predictors got
their first fires via `workflow_dispatch` with `force_release_date`,
which bypasses the gate entirely.

**Bit us:** discovered in Phase 3 while wiring boe/ukcpi/ukgdp push
lines. Fixed both Phase 2 (deifo) and Phase 3 (boe/ukcpi/ukgdp) in
one commit.

**How to apply:** Every new predictor prefix needs FOUR wiring
touchpoints in the worker: (1) MODEL_REGISTRY entry, (2) hardcoded
date array, (3) date-filter line in `refreshUpcomingMarquee`, (4)
`items.push` line in the same function. Grep for a previously-shipped
prefix (e.g. `ecb`) across all 4 touchpoints to verify parity before
declaring a new predictor "shipped."

### Rule 22: Country-branch pattern mints predictably

GBP branch was a copy-paste of EUR branch with three swapped regex
lines and one label. The country-branch refactor from Phase 2 pays
off here — total predictor addition (from decision to live) was ~1h
including smoke, model cards, worker deploy, and workflow_dispatch
verification. That's 3x the throughput vs Phase 1's per-predictor
build.

**How to apply:** When adding a new country in Phase 3+, the mental
recipe is:
1. Copy EUR/GBP branch in `predictionSlugFor`, swap regex + labels
2. Copy an emit_*.py + should_run_*.py + predict-*.yml as a set
3. Add 3-tuple of hardcoded dates (2026 + 2027 arrays)
4. Add 4-line wiring (see Rule 21)
5. Smoke via `workflow_dispatch` with `force_release_date`
6. Verify via `/public/models` + `/public/upcoming-marquee`
7. Ship model card + commit + push + wrangler deploy

Session cost is bottlenecked by GHA runtime + wrangler deploy, not by
code changes.

## What's outstanding (post-Phase 3)

**Phase 3.1 candidates:**
- UK Core CPI + services CPI splits (BoE's preferred underlying signals)
- ONS `api.ons.gov.uk` integration for UK GDP trend anchor + Index of
  Services + Industrial Production sub-models
- SONIA futures curve integration for BOE (replaces or augments spot anchor)

**Phase 4 candidates (deferred):**
- JP expansion — BOJ + Tankan + JP CPI + JP GDP (language barrier for
  BOJ docs still pending)
- AU/CA/CH — smaller markets but same pattern as EUR/GBP

**True Bayesian calibration** — still blocked on live scoring
resolutions accumulating. Chicken/egg from Phase 2 unchanged.

## Ledger of Phase 3 commits (chronological)

Session start (Phase 2 wrap): 6b0c4ed

Phase 3 predictor-repo commits:
- f612379 (rebased to 4def507) — Phase 3 UK trio: emit_boe/ukcpi/ukgdp +
  should_run + workflows + model cards + smoke reports

Worker-side companion commit in `far-reach/faractionradar-web`:
- 220d645 — calendar-worker: Phase 3 GBP branch (already deployed as
  wrangler version d5506e14-c277-4a50-9c71-2171c6786a95)

## Phase 3 completion status

**Rook-side shippable items: 100% complete.**

**Overall Phase 3 spec:**
- ✅ GBP expansion (3/3 predictors)
- ✅ Country-branch pattern extended to GBP (validates the refactor)
- ⚠️ ONS API integration (deferred to 3.1 — clean minor project)
- ⚠️ Core UK CPI split (deferred to 3.1)
- ⚠️ True Bayesian (still blocked on resolutions)

Effectively phase-closed for what's shippable this session.
