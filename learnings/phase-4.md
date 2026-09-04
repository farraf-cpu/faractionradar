# Phase 4 learnings — JP trio (BOJ + JP CPI + JP GDP)

Phase 4 opened 2026-09-04 (same-day after Phase 3 close, ~45min session).
Scope: 3 JPY predictors mirroring GBP trio pattern from Phase 3. Adds
JPY-branch routing to worker. Country coverage now: USD + EUR + GBP + JPY.

Read this before starting Phase 4.1 (e-Stat integration or Tankan
predictor) or Phase 5 (AU/CA/CH).

## What's live now (Phase 4 additions)

**JPY expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| boj | BOJ Policy Rate (MPC) | v2-outcome-distribution: consensus + FRED IRSTCI01JPM156N anchor, 25bp discretization | 18:15 + 02:30 T-0 |
| jpcpi | JP National Core CPI y/y | v1-simple-blend consensus-only (FRED JP CPI dead since 2022) | 18:20 + 22:30 T-0 |
| jpgdp | JP Preliminary GDP q/q | v1-simple-blend: consensus + FRED NGDPRSAXDCJPQ 4-qtr trend | 18:25 + 23:00 T-0 |

**Worker changes:**
- `predictionSlugFor` now routes by country: USD/EUR/GBP/**JPY** branches
- MODEL_REGISTRY: 52 → 55 entries
- Hardcoded arrays: BOJ_MEETINGS_2026/27, JPCPI_2026/27, JPGDP_2026/27
- Marquee pushes for boj/jpcpi/jpgdp

## Rules learned (or reinforced)

### Rule 23: The Discount-Rate-Dead pattern is universal on FRED

Third country in a row (Phase 3 UK, Phase 4 JP) where FRED's
`INTDSR{COUNTRY}M193N` series is discontinued and unusable as a
policy-rate anchor:
- UK: `INTDSRGBM193N` — frozen at 0.5% since 2013
- JP: `INTDSRJPM193N` — last observation 2017-04-01
- (US: `DFF` is live but that's not the equivalent series)

FRED's "OECD Immediate Rates <24h" series (`IRSTC{I}01{CTY}M156N`)
are LIVE and updating monthly — use these instead. Verified:
- UK: `IUDSOIA` (SONIA) — daily updates
- JP: `IRSTCI01JPM156N` — monthly updates

**How to apply:** For any new country's policy rate, skip the
Discount-Rate series entirely and go straight to OECD Immediate
Rates or the country's daily overnight benchmark. Don't waste smoke
tests on Discount-Rate variants — they're all discontinued.

### Rule 24: Country CPI dead-FRED is normal for non-USD/EUR

FRED covers US + EU CPI well but drops non-Western data:
- JP: `JPNCPIALLMINMEI`, `CPALTT01JPM659N`, `JPNCPICORMINMEI` — all
  discontinued 2022 with empty observations
- (UK: `CPALTT01GBM659N` still works — special case)

**How to apply:** For each new country's CPI, query FRED for a
recent observation FIRST. If empty/dead, ship consensus-only for v1
(deifo/ukgdp/jpcpi pattern) with a Phase X.1 target of native-API
integration:
- JP: e-Stat (api.e-stat.go.jp)
- UK: ONS (api.ons.gov.uk)
- CA: StatCan (statcan.gc.ca API)
- AU: ABS (data.gov.au)

### Rule 25: Marquee horizon (45d) means quarterly/annual series need
their own handling

JP GDP releases quarterly (~4x/year). The next release
(2026-11-16) is 73 days out. Marquee's `refreshUpcomingMarquee` uses
a 45-day horizon, so the JPGDP item is invisible until ~Oct 3.

Same issue exists for US ECI (quarterly), UK Interest Rate meetings
if they cluster, and any annual release.

**How to apply:** For low-frequency events, verify at least one
release is within 45 days when you first ship — otherwise the gate
script will always return "no marquee items, skip" until you get
into the horizon. If out-of-horizon at ship time, plan a re-verify
in ~30 days.

## What's outstanding (post-Phase 4)

**Phase 4.1 candidates:**
- e-Stat API integration for JP CPI trend anchor
- Tokyo Core CPI leading-indicator sub-model (releases ~1 month ahead)
- BOJ Tankan (large manufacturers diffusion index, quarterly, big JPY event)
- 10Y JGB futures curve for BOJ implied path

**Phase 5 candidates (deferred):**
- AU trio: RBA + AU CPI + AU GDP
- CA trio: BOC + CA CPI + CA GDP
- CH: SNB rate + Swiss CPI (smaller impact but liquid)

**True Bayesian calibration** — still blocked. Resolution accumulation
has been slow but is now spread across 55 predictor prefixes; empirical
variance should tighten over Q4.

## Ledger of Phase 4 commits (chronological)

Session start (Phase 3 wrap): 80d171d

Phase 4 predictor-repo commits:
- 60e1b45 (rebased to eb42638) — Phase 4 JP trio: emit_boj/jpcpi/jpgdp +
  should_run + workflows + model cards + smoke reports

Worker-side companion commit:
- 3d7c3d0 — calendar-worker: Phase 4 JPY branch (deployed as wrangler
  version 216b28b7-b80e-42d8-90b2-7c3c04e2dd9f)

## Phase 4 completion status

**Rook-side shippable items: 100% complete.**

**Overall Phase 4 spec:**
- ✅ JPY expansion (3/3 predictors)
- ✅ Country-branch pattern extended to JPY (validates recipe again)
- ⚠️ e-Stat API integration (Phase 4.1)
- ⚠️ Tokyo Core CPI leading indicator (Phase 4.1)
- ⚠️ BOJ Tankan (Phase 4.1)
- ⚠️ True Bayesian (still blocked on resolutions)

Effectively phase-closed for what's shippable this session. Country
coverage now: 4 (USD/EUR/GBP/JPY). Total predictors: 55.
