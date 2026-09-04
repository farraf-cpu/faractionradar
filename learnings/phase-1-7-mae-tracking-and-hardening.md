# Phase 1.7 learnings — MAE tracking + workflow hardening + stale-placeholder cleanup

Phase 1.7 shipped 2026-09-04 (pre-NFP), on top of Phase 1.6 (Tier 2
expansion). Scope: 4 split predictors (Core CPI/PPI/Retail + Export
Prices) bringing coverage to 45; workflow git-push race hardened;
`mae_observed` accuracy tracking scaffold built across 4 surfaces;
past-dated v1-beta placeholders purged from KV.

## What's live now (Phase 1.7 additions)

**Predictors (splits of parent releases; no new FRED release IDs):**

| Slug | Event | Cron UTC |
|------|-------|----------|
| corecpi | Core CPI m/m (ex food + energy) | 17:20 |
| coreppi | Core PPI m/m (Final Demand ex food + energy) | 17:25 |
| coreretail | Core Retail Sales m/m (ex Motor Vehicle & Parts) | 17:30 |
| exprices | Export Prices m/m | 17:35 |

**Reliability:**
- All 42 predict-*.yml wrap `git push` in 5-attempt retry loop with
  `git pull --rebase --autostash` between attempts.
- `.gitattributes` sets `predictions.jsonl merge=union` so parallel
  workflow appends never hit unresolved rebase conflicts.
- `seedBetaPlaceholders` skips past-dated events; `purgeStaleBetaPlaceholders`
  also deletes past-dated v1-beta records whose slug is still in the feed.

**MAE tracking (4 surfaces, all read-only aggregates over resolved KV records):**
- `/public/models` JSON — `mae_observed: {count, mae, hits, hit_rate}` per predictor
- `/calendar/models` HTML — "Observed MAE" row on each card
- `/public/status` JSON — `our_call_hits` + `our_call_hit_rate` rollup
- `/public/badge/hit-rate.svg` — README-embeddable proof-of-work badge

All start at `{count: 0, mae: null}` / "— (0 resolved)"; populate as
`scoreResolvedPredictions` writes `actual` + `colorSignal.proximity`
to each resolved KV record. Foundation for eventual /calendar/leaderboard
+ walk-forward MAE surface.

## Rules learned

### Rule 10: Parallel workflow git-push race needs merge=union, not just retry

Retry-with-rebase alone doesn't converge when 2+ workflows append to the
same file (predictions.jsonl). The rebase hits an unresolved conflict on
the append boundary, `git pull --rebase` fails with "you have unmerged
files", and every subsequent retry loop iteration re-fails.

Fix is at the merge-driver layer, not the retry-loop layer:
`.gitattributes` sets `predictions.jsonl merge=union`. Union driver
concatenates both sides — the correct semantic for an append-only ledger.

**Bit us:** Parallel dispatch of CorePPI + CoreRetail + ExportPrices
smoke tests all failed at git-push despite the retry loop existing.
Discovered because CorePPI + ExportPrices runs went red (worker POST
succeeded; only ledger commit failed).

**How to apply:** Any append-only JSONL / log file in a git repo written
by parallel processes needs `merge=union` in .gitattributes. Text files
with structured content (YAML config, JSON structured data) do NOT —
union would produce syntactically invalid output there.

### Rule 11: Past-dated v1-beta placeholders shadow real UX

Beta placeholders are "here's what our reader-facing schema looks like
for this slug type before the real predictor lands." They're valuable
for future events but MISLEADING for past events — a resolved event
should never show "awaiting predictor" in a reader-facing calendar cell.

**Bit us:** After landing 45 predictors, /calendar for Sep 1-3 events
still showed ~10 beta pills because seedBetaPlaceholders had populated
them earlier when predictors were still beta. purgeStaleBetaPlaceholders
had case (a) "slug no longer produced" but the events WERE still in the
FF feed as resolved rows.

**Fix:** `seedBetaPlaceholders` skips `event.date < today`.
`purgeStaleBetaPlaceholders` also deletes past-dated v1-beta records
regardless of legit-slug status.

**How to apply:** Any beta-placeholder mechanism must key on both slug
legitimacy AND date. A resolved event with no real predictor got no
prediction — full stop. Renderer should handle "no prediction" as a
first-class UX state, not fall back to a stale "coming soon" template.

### Rule 12: MAE tracking as read-only aggregate, not scoring-pipeline extension

Right pattern: separate the aggregate computation (`computeMaeByPrefix`)
from the scoring pipeline (`scoreResolvedPredictions`). Aggregation is a
single-pass KV scan over ALL resolved records; scoring is per-event
writeback triggered by fetch-calendar cron.

Coupling them (e.g. having scoreResolvedPredictions also maintain a
running MAE cache in KV) creates:
- Race conditions on the cache when scoring runs concurrently
- Reconciliation nightmares if any resolved record is manually corrected
- Extra failure modes in the write path

Read-only aggregate: any bug in the MAE code can't affect scoring
correctness. `mae_observed` is always a live derivation from ground
truth (the KV records). Trade-off: N KV reads per /public/models call.
Cache 60s already caps the cost.

## What's outstanding (post-Phase 1.7)

**Phase 2 (deferred, real accuracy upgrades):**
- CPI/Core CPI Bayesian — add Cleveland Fed nowcast (HTML scrape) +
  Dallas Fed trimmed-mean CPI sub-model (FRED PCETRIM12M6MMEAN or similar)
- FOMC outcome-distribution — probability distribution over {hold, cut25,
  cut50, hike25} using SEP + Fed funds futures + speaker hawkishness
- NFP additional sub-models — ADP correlation calibration, weekly claims
  trend, sector-decomp refinement

**Kalshi rollover fix (deferred, needs dedicated session):**
- Worker's direct Kalshi calls return 429 (Cloudflare IP pool blocked).
- KV snapshot from GHA (unblocked IP) still shows AUG focus event even
  after force-refresh, despite AUG NFP having released Aug 1.
- Need workflow_dispatch on fetch_kalshi.py with raw-event dump to
  understand why focus isn't rolling forward to SEP.

**Backtest infrastructure extension (deferred):**
- Only NFP has walk-forward backtest published at /calendar/backtest.
- Extending to Core CPI + FOMC needs historical FF consensus (not
  available via public API — would need scrape or manual seed).
- Trend-only backtest achievable now but weakens the accuracy claim
  (no consensus counterfactual).

**Coverage gaps (data-blocked):**
- Pending Home Sales (NAR PHSI) — proprietary, not on FRED
- NFIB Small Business Optimism — proprietary
- S&P Global PMI Composite/Mfg/Svc — proprietary
- All require paid feeds or scraping to unblock.

## Ledger of Phase 1.7 commits (chronological)

- `d89e18f` — retry-with-rebase on git push (41 workflows)
- `cc642e4` — .gitattributes predictions.jsonl merge=union
- `c9f4d21` — /public/models mae_observed field
- `e04e8d9` — /calendar/models Observed MAE row
- `f16e5c7` — /public/status our_call_hit_rate
- `0be967c` — /public/badge/hit-rate.svg
- `7f0a215` — past-dated beta placeholder purge + pill copy refresh
- `37538f0` — 4 split predictors (corecpi, coreppi, coreretail, exprices)

Worker-side companion commits in far-reach/faractionradar-web
(`calendar-worker/src/index.ts` + `src/render.ts` history).
