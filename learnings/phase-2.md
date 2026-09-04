# Phase 2 learnings — EUR expansion + accuracy upgrades

Phase 2 shipped 2026-09-04 (single day, ~half session on top of Phase 1.6
+ 1.7 base). Scope: 3 EUR predictors + Cleveland Fed accuracy upgrades
for 4 US inflation predictors + FOMC/ECB v2 outcome-distribution + T-0
release-day refresh mechanism across 24 predictors + country filter
refactor.

Read this before starting Phase 3 (UK/JP expansion). It builds on Phase
1 + 1.5-1.7 learnings.

## What's live now (Phase 2 additions)

**EUR expansion — 3 predictors:**

| Slug | Event | Approach | Cron UTC |
|------|-------|----------|----------|
| ecb | ECB Main Refinancing Rate (Deposit Facility Rate) | v2-outcome-distribution: consensus + FRED ECBDFR anchor, discretized into 25bp bucket probabilities | 17:45 + 11:15 T-0 |
| eurcpi | Eurozone CPI Flash Estimate y/y | v1-simple-blend: consensus + FRED CP0000EZ19M086NEST 3-mo mean | 17:50 + 08:00 T-0 |
| deifo | German IFO Business Climate | v1-simple-blend: consensus-only (IFO proprietary, OECD proxy scale-incompatible) | 17:55 + 07:00 T-0 |

**US inflation predictors upgraded with Cleveland Fed nowcast:**

| Slug | Version | Sub-models |
|------|---------|-----------|
| cpi | v1.2 | consensus + Cleveland Fed + Kalshi + Dallas trimmed-mean + FRED trend |
| corecpi | v1.2 | consensus + Cleveland Fed + Dallas trimmed-mean + FRED trend |
| pce | v1.1 | consensus + Cleveland Fed + FRED trend |
| corepce | v1.1 | consensus + Cleveland Fed + FRED trend |

**Rate-decision predictors upgraded to v2 outcome-distribution:**

| Slug | Version | Adds |
|------|---------|------|
| fomc | v2-outcome-distribution | Probability over {hike50, hike25, hold, cut25, cut50, cut75_plus, modal} discretized from point + sigma via normal CDF |
| ecb | v2-outcome-distribution | Same pattern applied to ECB |

**T-0 pre-release refresh** (~2h before print) added to 24 predictors:
NFP, CPI, FOMC, PCE, PPI, Retail, Durable, Housing, GDP, ADP, Claims,
CClaims, Core CPI/PPI/Retail/PCE, ISM Mfg/Svc, Confidence, UMich, JOLTS,
NewHome, Existing, ECB, EurCPI, DE IFO.

**Country filter refactor** in worker: `predictionSlugFor` now routes by
country. USD branch (unchanged, 45+ predictors) + EUR branch (3 predictors).
Adds explicit mappings for ecb, eurcpi, deifo prefixes.

## Rules learned

### Rule 15: Cleveland Fed nowcast alternates CPI + PCE cycles

Cleveland Fed publishes `nowcast_month.json` with 4 series: CPI Inflation,
Core CPI Inflation, PCE Inflation, Core PCE Inflation. They only fill the
relevant series depending on which release is next scheduled.

Currently in PCE cycle (Sep 22 PCE next). CPI cycle activates around
T-14 before each CPI release. Predictors reading Cleveland Fed must
soft-skip gracefully when their series is empty.

**Bit us:** Initially confused when Core PCE sub-model returned 0.13
during Aug 30 → Sep 22 window; realized data was there but for July
resolution, not next-print nowcast. Solution: always fetch latest
non-empty value; skip if none.

### Rule 16: OECD business confidence isn't a direct IFO substitute

Tried using OECD `BCCICP02DEM460S` (Germany Composite Business Confidence)
as anchor sub-model for German IFO predictor. OECD publishes on
percentage-balance scale (~-14 to +5, net positive vs negative responses).
IFO Business Climate publishes on an index level (~85-95, normalized to
2015=100).

These are directionally correlated but numerically incompatible. Blending
+55K IFO consensus with -14 OECD anchor gave -13.3 (nonsense).

**Bit us:** DE IFO v1 predictor failed initial smoke test with negative
value. Solution: dropped anchor sub-model, made DE IFO consensus-only.
Predictor soft-skips when FF consensus missing.

**How to apply:** Before using ANY sub-model with a different scale/methodology,
verify the value ranges match. A directional correlation is NOT enough for
inverse-MAE blending.

### Rule 17: Kalshi's `KX<SERIES>-YYMMM` refers to DATA month, not release month

Kalshi's event ticker naming initially confused me — thought AUG tickers
were stale because AUG NFP already released on Aug 1. Actually
`KXPAYROLLS-26AUG` is the AUGUST 2026 payroll DATA which releases on
Sep 4, 2026 (today).

Verified via GHA debug: KXPAYROLLS-26AUG has close_time
`2026-09-04T12:29:00Z` (1 minute before today's NFP release). It's the
current market, not stale.

**Bit us:** Wasted ~20 min investigating Kalshi rollover bug that didn't
exist. Learning: when a Kalshi ticker LOOKS wrong, check its
`close_time` before assuming stale.

### Rule 18: T-0 release-day refresh is a big trader-value win

Original design (per ROADMAP.md Q8) locked predictions at T-24h to
reduce noise and be trader-friendly. But user (real-money trader)
requested closer-to-event refresh — overnight Kalshi moves + last-hour
FF consensus revisions were being missed.

Shipped T-0 refresh at ~2h before each release (10:30 UTC for 12:30
releases, 12:00 UTC for 14:00 releases, seasonal for EUR times).
Applied to 24 top-tier predictors.

**How to apply:** For markets where users actively bet, prefer FRESH
predictions over LOCKED predictions. The "trader-friendly settled call"
argument was theoretical; real traders want the freshest signal.

### Rule 19: Discretized outcome-distribution from point + sigma is a legitimate v2 upgrade

For rate-decision predictors (FOMC, ECB), the sub-models emit point
estimates but traders think in discrete outcomes ({hold, hike25, cut25,
etc}). Bridge: assume the posterior is `N(point, sigma^2)` and integrate
that normal over 25bp buckets to get probability per outcome.

Not "true" Bayesian (sigma is prior-based MAE not empirical variance) but
gives traders discrete probabilities to size positions against expected
value.

Implemented via `compute_outcome_distribution()` in emit_fomc.py + emit_ecb.py.
Payload field: `ourCall.outcomeDistribution: {hike50, hike25, hold, cut25,
cut50, cut75_plus, modal}`. Worker's renderPredictionDetail displays as
horizontal probability bars.

## What's outstanding (post-Phase 2)

**Phase 3 candidates (deferred, real projects):**
- UK expansion — BOE rate + UK CPI + UK GDP predictors (same country-branch
  pattern as EUR)
- JP expansion — BOJ + Tankan + JP CPI + JP GDP (language barrier for BOJ
  docs, flag ahead)
- Additional US 3-stars — NFIB SBOI (proprietary), Case-Shiller y/y (have
  m/m equiv already), Powell speeches (qualitative)

**True Bayesian calibration** — needs live scoring resolutions to accumulate.
Chicken/egg: sub-model MAE priors from historical backtest are OK for
now but true posterior variance requires empirical data.

**FOMC v2.1 upgrades** — currently discretization is normal-CDF over
market-anchored point. Could improve with:
- Real Kalshi ladder-per-outcome (each 25bp outcome has its own market;
  we could read yes-prices directly instead of discretizing)
- SEP dot-plot median from most recent SEP release
- Speaker-hawkishness rolling index over Fed speeches since last meeting

**UI Country/Category filters** — Vega's territory. Data already in
worker (/public/models supports EUR; /public/upcoming-marquee includes
EUR events).

## Ledger of Phase 2 commits (chronological)

Session start: b8eb0bf (Phase 1.7 wrap)

Phase 2 commits:
- 74aedae — corecpi: Cleveland Fed sub-model (v1.1)
- d0f064f + f53ef98 — cpi: Cleveland Fed + version bump v1.2
- 2e3d4ec — pce: Cleveland Fed sub-model (v1.1)
- 801d828 + f9608f1 — corepce: new predictor v1.1
- e4169ac — worker: country filter refactor for EUR
- 6515de6 — ecb: new predictor v1
- 503adf1 — worker: register ECB + hardcoded meeting dates
- 78ace31 — worker: re-add eurcpi to MODEL_REGISTRY (concurrent-edit race)
- 752d13a — eurcpi: new predictor v1
- 19eba7b + 65e2910 — deifo: new predictor v1 + fix (consensus-only)
- eb2b710 — worker: register DE IFO + hardcoded release dates
- 31c40b6 — corecpi: Dallas trimmed-mean added (v1.2)
- 5d8dd3e — nfp: T-0 pre-release refresh cron
- 0f43dc2 — cpi + fomc: T-0 refresh
- bd9af10 — 18 more predictors: T-0 refresh batch
- d2b6df9 — 3 EUR predictors: T-0 refresh
- 44d45d2 + 42e0744 — Kalshi debug logging (added + reverted after Rule 17)
- b14a117 — fomc: v2-outcome-distribution
- b262218 — worker: renderOutcomeDistribution on prediction detail page
- 496a5e7 — ecb: v2-outcome-distribution
- c7af813 — docs: FOMC + ECB model cards refreshed for v2
- ef8df10 — docs: CPI + Core CPI cards refreshed for v1.2
- 1093dfc — docs: PCE + Core PCE cards refreshed

Worker-side companion commits in `far-reach/faractionradar-web`.

## Phase 2 completion status

**Rook-side shippable items: 100% complete.**

**Overall Phase 2 spec (per ROADMAP.md §5):**
- ✅ EUR expansion (3/3 predictors)
- ✅ Cleveland Fed nowcast integration (bonus, not in original spec)
- ✅ CPI/FOMC beta → live upgrade (CPI v1.2 + FOMC v2)
- ⚠️ True Bayesian (partial — inverse-MAE is Bayesian-adjacent; empirical variance blocked on resolutions)
- ⚠️ UI Country + Category filters (Vega's territory)

Effectively phase-closed for what's shippable this session.
