# Phase 1.5 learnings — CPI + FOMC live

Phase 1.5 shipped 2026-09-03, day after Phase 1. Scope: CPI + FOMC live
predictors via `predict-cpi.yml` + `predict-fomc.yml` GHA workflows, both
running the new `v1-simple-blend` model. First-fire dates: CPI T-7 fires
2026-09-04 for the Sep 11 event; FOMC T-7 fires 2026-09-10 for the Sep 17
meeting.

Read this before starting Phase 2 (bayesian upgrades for CPI/FOMC + EUR
expansion). It builds on Phase 1's rules, doesn't replace them.

## What is live now

- `emit_cpi.py` + `.github/workflows/predict-cpi.yml` — inverse-MAE blend of
  consensus (0.08pp) + Kalshi implied m/m (0.12pp) + FRED CPIAUCSL 6-mo
  trend (0.15pp). Model version tag `v1-simple-blend`.
- `emit_fomc.py` + `.github/workflows/predict-fomc.yml` — inverse-MAE blend
  of Kalshi implied rate (0.05pp) + optional consensus (0.07pp) + FRED
  DFEDTARU current-rate anchor (0.25pp). Same version tag.
- `scripts/should_run_cpi.py` + `scripts/should_run_fomc.py` — gates hit the
  worker's `/public/upcoming-marquee` endpoint (FRED release calendar, 45-day
  horizon) to resolve the next release date, then exit early on non-cadence
  days. Cadence is same T-{7,4,3,2,1} as NFP.
- `docs/cpi-model-card.md` + `docs/fomc-model-card.md` refreshed from v1-beta
  placeholder to v1-simple-blend spec with Phase 2 targets called out.
- Worker's `/public/models` endpoint enumerates all three live predictors.
- Worker's `/calendar/roadmap` reflects Phase 1 + 1.5 shipped, Phase 2 + 3+
  planned.

Verified end-to-end via `workflow_dispatch` on 2026-09-03: CPI +0.1% m/m
prediction landed at `events:predictions:cpi-2026-09-11`; FOMC 3.96% target
rate landed at `events:predictions:fomc-2026-09-17`.

## Rules that came out of Phase 1.5

### 1. Don't gate the predict step on consensus availability.

Initial `predict-cpi.yml` had `if: steps.consensus.outputs.skip != 'true'`
on the predict step. Meant "wait until FF publishes the forecast." Cost: we
were sitting on runnable market + trend data because FF hadn't updated yet.

Fix: consensus fetch is best-effort. Sets `consensus_pct` if present,
`consensus_available=false` otherwise. `emit_cpi.py` already had the right
soft-skip logic — only bails if ALL three sub-models are missing. Removed
the workflow-level gate; let the emitter decide.

This matters because Kalshi implied is often live for the reference month
BEFORE FF publishes its forecast for the release week. Missing that window
is a self-inflicted delay.

### 2. Module-level side effects break smoke tests.

`src/final_report.py` had a module-level line:

```python
CONSENSUS_NFP_K = _resolve_consensus()
```

`_resolve_consensus()` raises `RuntimeError` in GHA if `NFP_CONSENSUS_K` is
missing (correct behavior — refuse to publish a prediction anchored to a
stale hardcoded value). But this fires on any `import src.final_report`,
which the `smoke.yml` workflow does deliberately to sanity-check that all
modules load.

Fix: defer to inside `report()` with `global` re-assignment. The guard
still fires at prediction time; smoke just wants an importable module.

Rule: any module-level constant whose initializer reads env vars OR calls
network / disk should be deferred to first-use. Especially guards that
`raise` — smoke tests will trip them.

### 3. `betaPlaceholderFor` copy is a UX contract, keep it current.

The worker seeds "awaiting predictor" placeholders for CPI/FOMC slugs when
no prediction exists yet. Original text was "model not yet trained · beta
shipping Phase 2 (EUR expansion)." That was accurate when only NFP was
live. Once CPI + FOMC v1-simple-blend shipped, the text became misleading:
readers would see it in the ~few-minute window between placeholder seed and
the first real emit landing, and conclude no model exists.

Updated to "awaiting predictor · v1-simple-blend fires within T-7 cadence."
Rule: any time a Phase transition ships a model that changes what's true
about a placeholder, update the placeholder in the same commit set.

### 4. `predictionSlugFor` regex must be tight OR the placeholder purge won't clean up.

`FOMC Member Barr Speaks` (a speech, not a rate decision) was leaking into
the FOMC slug space in a earlier Phase 1 build because the regex matched
anything with "FOMC". Later tightened to only match `federal funds rate` /
`fomc rate statement` / `fomc statement`. But a stale
`events:predictions:fomc-2026-09-01` record persisted in KV because the
purge only removes FUTURE-dated placeholders whose slug no longer maps.
Past-dated stale placeholders survive.

Manually deleted via `wrangler kv key delete`. Later that day I extended
`purgeStaleBetaPlaceholders` in the worker to also purge past-dated illegit
slugs — so this class of orphan self-heals now.

### 5. Scoring proximity thresholds must be scale-aware.

The worker's `scoreResolvedPredictions` ranks each predictor by |value - actual|
and assigns a "closest / close / off" pill. The "close" threshold was:
```
closeThreshold = max(bestDist * 1.2, bestDist + 5)
```

The `+5` fallback was calibrated for NFP (K-jobs scale). For CPI + FOMC,
which are on a %-points scale (typical actual values 0.0-0.4 for CPI m/m,
3.75-5.00 for FOMC rate), a +5 threshold would make EVERY predictor "close"
regardless of quality — 5 percentage points is enormous.

Fix: read the slug prefix, use a scale-aware minimum. NFP keeps +5; CPI +
FOMC use +0.05pp (about +5 basis points). Ratio threshold (`bestDist * 1.2`)
stays the same across scales.

This bit us at *design time*, not runtime — no CPI/FOMC had resolved yet
when I caught it during a manual code review. If it had shipped and the
first CPI resolution painted everyone "close", the track record page would
have looked useless. Worth catching now.

**Rule for Phase 2:** every time we add a new event type with a different
value scale (%, K jobs, rate, %-YoY, absolute levels), audit
`parseNumericValue` (does it parse the value format?) AND the scoring
threshold (does the +N fallback make sense at this scale?).

## What worked well in Phase 1.5

- Reusing `/public/upcoming-marquee` as the gate-script data source. No new
  worker code needed for the CPI/FOMC gates.
- Reusing the worker's `/public/kalshi-implied` endpoint. Same ladder-to-K
  logic serves all three predictors; each predictor just reads the right
  slug (`nfp` / `cpi` / `fomc`).
- Reusing the same `/upload` schema. `PredictionRecord.ourCall` fits CPI's
  `+0.1%` and FOMC's `3.96%` as `value: string` without change. No worker-
  side schema migration.
- Manual `workflow_dispatch` with `force_release_date` + `force_days_out`
  inputs made smoke-testing painless. Left them in the CPI/FOMC workflows
  for future backfills.

## Phase 2 target — updated from Phase 1's plan

**CPI v2-bayesian-blend** — same architecture as NFP:
- Cleveland Fed inflation nowcast (public, daily updates, ~0.06pp MAE)
- Trimmed-mean CPI (FRB Dallas 8% trimmed series) as mean-reverting anchor
- Shelter component tracker (separate release cycle, biggest post-COVID
  error driver)
- + existing consensus + market + trend sub-models
- Target MAE < 0.10pp on headline m/m over ~40 post-COVID months

**FOMC v2-outcome-distribution** — probability distribution over discrete outcomes:
- {hold, cut25, cut50, hike25} probability per outcome
- Fed funds futures implied probability from CME (may need scraping)
- SEP dot-plot median from most recent SEP release
- Speaker-hawkishness rolling index over Fed speeches since last meeting
- Data surprise index (CPI + NFP + PCE surprises since last meeting)
- Payload adds `outcomeDistribution` field alongside scalar `value` for
  backwards-compat with the current schema

**EUR expansion** — ECB rate decisions, Eurozone CPI flash, DE IFO. New
slug prefixes (`ecb`, `eur-cpi`, `de-ifo`) + new gate scripts + new emit
scripts. Follow the same v1-simple-blend pattern first (consensus + market
+ trend/anchor), then upgrade to bayesian as Phase 2 progresses.

## Ledger of Phase 1.5 commits (chronological)

- `8d15140` — CPI v1-simple-blend live predictor
- `d4e3e33` — FOMC v1-simple-blend live predictor
- `184a736` — defer NFP_CONSENSUS_K resolution to report() call (smoke fix)
- `96923ca` — CPI always-run (don't gate on missing consensus)

Worker-side companion commits are in the calendar-worker repo. See
`calendar-worker/src/index.ts` history for the Phase 1.5 worker changes.
