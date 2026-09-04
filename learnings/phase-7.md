# Phase 7 learnings — NZ trio (RBNZ + NZ CPI + NZ GDP)

Phase 7 opened 2026-09-04 (same-day after Phase 6, ~30min session).
Scope: 3 NZD predictors. Country coverage: 7 majors.

## What's live now (Phase 7 additions)

**NZD expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| rbnz | RBNZ OCR (MPC) | v2-outcome-distribution: consensus + IR3TIB01NZM156N anchor (MAE inflated 0.30pp for term premium) | 18:30 + 01:30 T-0 |
| nzcpi | NZ CPI y/y (quarterly) | v1-simple-blend consensus-only (CPALTT01NZQ659N dead) | 18:35 + 22:00 T-0 |
| nzgdp | NZ GDP q/q (quarterly) | v1-simple-blend consensus-only (NGDPRSAXDCNZQ doesn't exist) | 18:40 + 22:30 T-0 |

**Worker changes:**
- `predictionSlugFor` now routes by country: USD/EUR/GBP/JPY/AUD/CAD/**NZD** branches
- MODEL_REGISTRY: 61 → 64 entries
- Hardcoded arrays: RBNZ_MEETINGS_2026/27, NZCPI_2026/27, NZGDP_2026/27
- Marquee pushes for rbnz/nzcpi/nzgdp

## Rules learned

### Rule 29: Small-country FRED coverage drops off a cliff

NZ has significantly worse FRED coverage than G7:
- IRSTCI01NZM156N (OECD Immediate <24h) — LIVE but stale 2 years
- CPALTT01NZQ659N (CPI y/y quarterly) — discontinued 2023
- NGDPRSAXDCNZQ (real GDP quarterly) — doesn't exist at all

Fallback path: `IR3TIB01NZM156N` (3-mo interbank) is live but carries
term premium. Solution: use it with MAE=0.30pp (2x the normal 0.15
term rate MAE) to reduce weight in the blend. Consensus dominates
when present.

For CPI + GDP: consensus-only pattern (deifo/jpcpi/nzcpi/nzgdp all
follow this).

**How to apply:** When entering a small G10 country (NZ/CH/SE/NO),
expect FRED coverage to be 30-50% of what US/UK/JP have. Ship
consensus-only for everything that lacks a live series; use inflated-MAE
term-rate fallbacks for rate anchors; document native-API integration
as Phase X.1 target.

### Rule 30: Sub-model MAE weighting is a valid workaround for imperfect anchors

RBNZ IR3TIB01NZM156N anchor has known ~15-25bp term premium above
the actual OCR. Instead of dropping the sub-model, inflate MAE:
- Term-premium anchor: MAE 0.30pp (vs 0.15pp for a clean overnight
  proxy like IUDSOIA/SONIA or IRSTCI01AUM156N)
- Consensus: MAE 0.05pp (unchanged)

The blend now weights consensus 6x more than anchor. When consensus
present, prediction snaps to it; when absent, anchor dominates but
users see wider CI and "no consensus" lean.

**How to apply:** Rather than binary include/exclude, use MAE as a
knob. Imperfect signals still contribute at low weight — better than
dropping them entirely and losing coverage when the primary signal
is missing.

## What's outstanding (post-Phase 7)

**Phase 7.1 candidates:**
- StatsNZ Infoshare API integration (real anchors for nzcpi/nzgdp)
- NZ OIS curve for RBNZ implied OCR path (eliminates term premium)

**Phase 8 candidates (deferred):**
- CH: SNB + Swiss CPI (similar thin FRED, same recipe as NZ)
- Emerging: KR / MX / SG / ZA (larger effort, thin data)

**True Bayesian** — still blocked.

## Progression timeline (all same-day 2026-09-04)

- Phase 2 (EUR) — 4-6h (recipe creation)
- Phase 3 (UK) — 1h (recipe validation)
- Phase 4 (JP) — 45m
- Phase 5 (AU) — 40m
- Phase 6 (CA) — 30m
- Phase 7 (NZ) — 30m (identical to Phase 6)

Recipe is at throughput floor. Bottleneck: wrangler deploy (~15s) +
fetch-calendar wait (~1min) + 3 GHA smoke runs (~2min parallel).
Code changes are <5min.

## Ledger of Phase 7 commits

Session start (Phase 6 wrap): 074aa53

Phase 7 predictor-repo commits:
- 6e99195 — Phase 7 NZ trio: emit_rbnz/nzcpi/nzgdp + should_run +
  workflows + model cards + smoke reports

Worker-side companion commit:
- b5d761a — calendar-worker: Phase 7 NZD branch (deployed as wrangler
  version 5d1bc25d-ec0a-4a33-bc9d-bc436aced6a2)

## Phase 7 completion status

**Rook-side shippable items: 100% complete.**

- ✅ NZD expansion (3/3 predictors)
- ✅ Recipe validated at 7 countries
- ⚠️ StatsNZ Infoshare API integration (Phase 7.1)
- ⚠️ True Bayesian (blocked)

Country coverage: 7 (USD/EUR/GBP/JPY/AUD/CAD/NZD). Total predictors: 64.
