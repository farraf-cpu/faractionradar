# Phase 6 learnings — CA trio (BOC + CA CPI + CA GDP)

Phase 6 opened 2026-09-04 (same-day after Phase 5 close, ~30min session
— fastest phase yet thanks to fully-proven recipe). Scope: 3 CAD
predictors mirroring AUD trio pattern. Country coverage: 6 majors.

Read this before Phase 7 (CH/NZ) or Phase 6.1 (StatCan API integration).

## What's live now (Phase 6 additions)

**CAD expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| boc | BOC Overnight Rate | v2-outcome-distribution: consensus + FRED IRSTCI01CAM156N anchor + 25bp discretization | 18:30 + 01:30 T-0 |
| cacpi | CA CPI y/y (monthly) | v1-simple-blend: consensus + FRED CPALTT01CAM659N 3-mo mean | 18:35 + 22:00 T-0 |
| cagdp | CA Monthly GDP m/m | v1-simple-blend consensus-only (StatCan not on FRED) | 18:40 + 22:30 T-0 |

**Worker changes:**
- `predictionSlugFor` now routes by country: USD/EUR/GBP/JPY/AUD/**CAD** branches
- MODEL_REGISTRY: 58 → 61 entries
- Hardcoded arrays: BOC_MEETINGS_2026/27, CACPI_2026/27, CAGDP_2026/27
- Marquee pushes for boc/cacpi/cagdp

## Rules learned (or reinforced)

### Rule 27 — Discount-Rate-Dead confirmed 4-country universal

Fourth country in a row confirming: UK/JP/AU/**CA** all have
discontinued `INTDSR{X}M193N` series. This is the OECD FRED convention
for discount rates — they got shipped in the early 2010s and no
country's central bank has updated them since.

Series to skip on all future country builds:
- INTDSRGBM193N (UK) — dead
- INTDSRJPM193N (JP) — dead
- INTDSRAUM193N (AU) — dead
- INTDSRCAM193N (CA) — dead

Use OECD `IRSTCI01{CTY}M156N` (Immediate Rates <24h) instead. Verified
LIVE:
- IRSTCI01JPM156N (JP)
- IRSTCI01AUM156N (AU)
- IRSTCI01CAM156N (CA)
- (UK uses SONIA-specific IUDSOIA)

### Rule 28 — Sed substitutions collide with substring matches

Doing `sed 's/ONS/StatCan/g'` on emit_ukgdp.py → emit_cagdp.py
accidentally rewrote `CONSENSUS` to `CStatCanENSUS` because `ONS`
appears inside `CONSENSUS`. Also `s/AU /CA /` protected against
matching `AUD` etc., but the 3-letter code cases still need care.

**How to apply:** For predictor-scaffolding sed runs, always guard
substitutions with word boundaries (`\bONS\b` instead of `ONS`) OR
grep-verify the output before committing. Cost of bug in this case
was 30s (grep + manual re-sed) but had CI caught it, would have
been a workflow failure.

## What's outstanding (post-Phase 6)

**Phase 6.1 candidates:**
- CPI-trim / CPI-median / CPI-common (BOC's preferred core measures)
- StatCan WDS API integration for real monthly GDP anchor
- BAX 3-month bankers' acceptance futures for BOC implied path

**Phase 7 candidates (deferred):**
- CH: SNB + Swiss CPI (smaller market but liquid, EUR-adjacent)
- NZ: RBNZ + NZ CPI + NZ GDP (small but full G10 coverage)
- KR / MX / ZA: emerging majors (bigger effort, lower priority)

**True Bayesian calibration** — still blocked on resolutions.

## Ledger of Phase 6 commits

Session start (Phase 5 wrap): fd012c0

Phase 6 predictor-repo commits:
- 1126dfb — Phase 6 CA trio: emit_boc/cacpi/cagdp + should_run +
  workflows + model cards + smoke reports

Worker-side companion commit:
- 78398d6 — calendar-worker: Phase 6 CAD branch (deployed as wrangler
  version 2ee63d35-7e43-4e83-bea3-3106f9a313ed)

## Phase 6 completion status

**Rook-side shippable items: 100% complete.**

- ✅ CAD expansion (3/3 predictors)
- ✅ Country-branch pattern extended (6th country, ~30min build)
- ⚠️ StatCan WDS API integration (Phase 6.1)
- ⚠️ True Bayesian (blocked)

Country coverage: 6 (USD/EUR/GBP/JPY/AUD/CAD). Total predictors: 61.

**Progression cost timeline:**
- Phase 2 (EUR) — 4-6h (first country expansion, refactor)
- Phase 3 (UK) — ~1h (recipe validation)
- Phase 4 (JP) — ~45min
- Phase 5 (AU) — ~40min
- Phase 6 (CA) — ~30min (fully-proven recipe)

Phases 7+ should hit ~25-30min each. Bottleneck is FRED verification
+ wrangler deploy + GHA smoke — not code.
