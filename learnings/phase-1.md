# Phase 1 learnings

Phase 1 shipped 2026-09-02. Scope: NFP live prediction end to end, CPI and FOMC beta placeholders on the worker side. This file is meant to be read by whoever writes Phase 2 (and every subsequent phase) before starting.

## What is live now

- `scripts/fetch_calendar.py` runs on GHA cron and POSTs normalized ForexFactory events to the calendar worker's `/upload-events`.
- `emit.py` runs on GHA cron via `predict-nfp.yml`, produces a blended NFP forecast, POSTs it to `/upload`, writes a per-run report to `reports/YYYY-MM/nfp-t-N.md`, appends a row to `predictions.jsonl`, and commits both back to this repo.
- First real prediction landed as commit `0eed25c`: NFP T-2 for the 2026-09-04 release. Point +90K, 68% CI [+59, +121].
- The worker's `/?prediction=<slug>` returns the stored `ourCall` and `grandMedian` blocks for consumption by the FAR web `/calendar` page.

## Rules to carry into Phase 2

These are the ones we paid a real cost to learn. Do not re-learn them.

### 1. Every outbound POST from GHA to a Cloudflare-fronted endpoint needs a browser User-Agent.

Cloudflare's bot filter returns "error 1010" for requests whose UA starts with `Python-urllib/` or `python-requests/`. This looks like a network failure, not a policy block, because the response body is HTML.

Set `user-agent: Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0` on the request. Local dev succeeds without it because residential IPs are treated more leniently, so local success does not imply GHA success.

Bit us twice in Phase 1: once in `fetch_calendar.py` POST to `/upload-events` (fixed in `17d5c08`), once in `emit.py` POST to `/upload` (fixed in `65f17e1`). If Phase 2 adds any new outbound POST from GHA, apply this rule at write time.

### 2. FRED public graph endpoint is unreachable from GHA. Use the API.

`https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}` read-times-out at 30s from GHA runners for every series (Cloudflare filtering on the graph subdomain). No amount of retries or backoff will fix it.

Use `https://api.stlouisfed.org/fred/series/observations?series_id={sid}&api_key={FRED_API_KEY}&file_type=json` instead. The API subdomain is not blocked. Rate limit is 120 req/min per key, which is fine for the ~34-series full refresh.

If Phase 2 adds new data sources, check each one from a GHA runner before wiring them into the model. A quick `curl` in a dispatch-only workflow is faster than debugging a full predictor run.

### 3. Runtime values that vary per release must come from env vars, not module constants.

`build_features.py` originally pinned `PREDICTION_MONTH = pd.Timestamp("2026-07-01")`. It kept producing July predictions after the workflow started passing `NFP_RELEASE_DATE=2026-09-04`. Fixed by deriving PREDICTION_MONTH from the env var, with the constant kept as a local-dev fallback.

For Phase 2, any new predictor should read its reference date, cadence slot, model version, and any other per-release parameters from env at import time. Never let module state and workflow state disagree.

### 4. Paths must be repo-relative, not machine-absolute.

Every module in `src/` had `C:/Predictor/...` hardcoded (23 references across 11 files). That worked in local dev on the author's laptop and immediately exploded on the Linux runner. Rewrote with `Path(__file__).resolve().parent.parent / "data" / ...`.

For Phase 2 predictor modules: same rule from day one. Anchor to `__file__`, not to a fixed disk layout.

## Non-blocking followups from Phase 1

Carry these into Phase 2 when convenient. None block the current pipeline.

- `fetch_calendar.py` gets `nextWeek: HTTP 404` from ForexFactory. `thisWeek` covers 7 days ahead including the next NFP, so predictions are not affected, but the fallback source URL is worth investigating.
- `run.py` was already threaded to accept `NFP_RELEASE_DATE` via env, but the BANNER string was hardcoded. Fixed for NFP. If Phase 2 adds CPI or FOMC live models, mirror the same env-driven pattern from the start.
- Fixing the paths surfaced that `final_report.py:239` writes `reports/final_forecast_YYYY_MM.md` alongside the versioned `reports/YYYY-MM/nfp-t-N.md`. Two report locations for the same run is redundant. Consolidate in Phase 2.

## Verification pattern that worked

For any future release-date event, this smoke sequence caught every regression in Phase 1:

1. `gh workflow run <fetch-workflow> --repo farraf-cpu/faractionradar`, watch to green.
2. `curl "$WORKER/?key=$CAL_KEY&read"` and grep for the expected event in the returned array.
3. `gh workflow run <predict-workflow> --repo farraf-cpu/faractionradar`, watch to green.
4. `curl "$WORKER/?key=$CAL_KEY&prediction=<slug>"` and confirm `ourCall` + `grandMedian` + `receivedAt` are populated.
5. `git fetch` and confirm a bot commit landed with the report + ledger row.

Any of the five failing narrows the bug to a specific layer.

## Attempt log (Phase 1 first-ship)

Useful for future capacity planning. The scaffold was mostly written before this session; the failures below are integration issues, not model issues.

| Attempt | Run ID | Failure | Root cause |
|---------|--------|---------|------------|
| 1 (from prior session) | fetch-calendar first dispatch | POST to `/upload-events` rejected 1010 | UA header missing (Rule 1) |
| 2 | fetch-calendar 33618080069 | ok | UA fix landed |
| 3 | predict-nfp 33618394103 | 18m timeout at FRED refresh | Wrong FRED endpoint (Rule 2) |
| 4 | predict-nfp 33620995975 | predict step 49s, POST rejected exit 3 | UA header missing on emit.py POST (Rule 1, again) |
| 5 | predict-nfp 33621457578 | green in 66s | all four rules satisfied |

Total time from picking up the loose thread to a live prediction in the worker: about 40 minutes of active work across four commits.
