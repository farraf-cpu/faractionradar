# Phase 5 learnings — AU trio (RBA + AU CPI + AU GDP)

Phase 5 opened 2026-09-04 (same-day after Phase 4 close, ~40min session).
Scope: 3 AUD predictors mirroring JPY trio pattern. Adds AUD-branch to
worker. Country coverage: USD + EUR + GBP + JPY + AUD (5 majors).

Read this before Phase 5.1 (CA trio) or Phase 6 (CH/NZ).

## What's live now (Phase 5 additions)

**AUD expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| rba | RBA Cash Rate (MPC) | v2-outcome-distribution: consensus + FRED IRSTCI01AUM156N anchor + 25bp discretization | 18:30 + 01:30 T-0 |
| aucpi | AU CPI y/y (quarterly) | v1-simple-blend: consensus + FRED CPALTT01AUQ659N previous-quarter | 18:35 + 22:00 T-0 |
| augdp | AU GDP q/q (quarterly) | v1-simple-blend: consensus + FRED NGDPRSAXDCAUQ 4-qtr trend | 18:40 + 22:30 T-0 |

**Worker changes:**
- `predictionSlugFor` now routes by country: USD/EUR/GBP/JPY/**AUD** branches
- MODEL_REGISTRY: 55 → 58 entries
- Hardcoded arrays: RBA_MEETINGS_2026/27, AUCPI_2026/27, AUGDP_2026/27
- Marquee pushes for rba/aucpi/augdp

## Rules learned (or reinforced)

### Rule 26: Not all "policy rate proxies" are equal — check term premium

Initial RBA smoke used `IR3TIB01AUM156N` (3-month Interbank Rate AU) as
anchor, which returned 4.46%. Real RBA cash rate ~4.10%. The 30bp gap
is the interbank term premium (3-mo tenor vs overnight cash).

Result: smoke gave "-69bp cut vs current rate" lean when RBA was
actually likely to hold. Outcome distribution overweighted cut75+ at
86%. Distribution shape was correct math but the anchor was 30bp
mis-calibrated.

**Fix:** Swapped to `IRSTCI01AUM156N` (OECD Immediate Rates <24h AU) —
tracks cash rate within 5-10bp. Re-smoke: 4.35% hold 98%. Realistic.

**How to apply:** For rate-decision anchors, prefer *overnight* rate
series (SONIA/EFFR-equivalent/Immediate Rates <24h) over *term* rates
(1-month, 3-month interbank). Term rates carry a premium that biases
the anchor upward, which cascades into the outcome distribution as
false "expected cut" signals. The OECD Immediate Rates family
(IRSTCI01{CTY}M156N) is the safe default for non-US countries.

### Rule 27: Rule 23 (Discount-Rate-Dead) is truly universal

Third country in a row confirming: UK/JP/AU all have discontinued
INTDSR{CTY}M193N series. Assume the same for CA, NZ, CH, KR, etc.
Skip Discount Rate variants entirely on new-country builds and go
straight to OECD Immediate Rates <24h.

Country-specific overnight rate series that DO work (verified):
- UK: `IUDSOIA` (SONIA) — daily updates
- JP: `IRSTCI01JPM156N` — monthly updates
- AU: `IRSTCI01AUM156N` — monthly updates
- (US: `DFF` — daily, ~1bp of EFFR)

## What's outstanding (post-Phase 5)

**Phase 5.1 candidates:**
- Trimmed-mean AU CPI split (RBA's preferred underlying gauge)
- ASX 30-day interbank cash rate futures for RBA implied path
- Monthly AU CPI indicator as leading sub-model

**Phase 6 candidates (deferred):**
- CA trio: BOC + CA CPI + CA GDP (all FRED-covered, ~30min build)
- CH: SNB rate + Swiss CPI (smaller but liquid)
- NZ: RBNZ + NZ CPI + NZ GDP

**True Bayesian calibration** — still blocked.

## Ledger of Phase 5 commits (chronological)

Session start (Phase 4 wrap): 6cd7cce

Phase 5 predictor-repo commits:
- b5eaf33 — Phase 5 AU trio: emit_rba/aucpi/augdp + should_run +
  workflows + model cards + smoke reports

Worker-side companion commit:
- 5dcb1b5 — calendar-worker: Phase 5 AUD branch (deployed as wrangler
  version 270c7829-a922-4b81-bd15-46b22e34cb6a)

## Phase 5 completion status

**Rook-side shippable items: 100% complete.**

- ✅ AUD expansion (3/3 predictors)
- ✅ Country-branch pattern extended to AUD (5th country, same recipe)
- ⚠️ ASX cash rate futures curve (Phase 5.1)
- ⚠️ True Bayesian (blocked)

Country coverage: 5 (USD/EUR/GBP/JPY/AUD). Total predictors: 58.
