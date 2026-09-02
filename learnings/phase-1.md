# Phase 1 learnings

Phase 1 shipped 2026-09-02. Scope: NFP live prediction end to end, CPI and FOMC beta placeholders on the worker side. This file is meant to be read by whoever writes Phase 2 (and every subsequent phase) before starting.

## What is live now

- `scripts/fetch_calendar.py` runs on GHA cron and POSTs normalized ForexFactory events to the calendar worker's `/upload-events`.
- `emit.py` runs on GHA cron via `predict-nfp.yml`. Before the model runs, a workflow step pulls the live ForexFactory forecast from the worker (`/?read`), parses it, and passes it as `NFP_CONSENSUS_K`. `final_report.py` hard-fails in GHA if this env var is missing so a stale prediction cannot ship silently.
- After the model runs, `emit.py` POSTs the blended forecast to `/upload`, writes a per-run report to `reports/YYYY-MM/nfp-t-N.md`, appends a row to `predictions.jsonl`, and commits both back to this repo.
- Corrected prediction lives at commit `f62e174`: NFP T-2 for the 2026-09-04 release. Point +80K, 68% CI [+50, +111], lean MODESTLY ABOVE consensus (live consensus +55K). This superseded an earlier stale-input prediction of +90K falsely labeled "in line with consensus" (`0eed25c`, corrected within an hour).
- The worker's `/?prediction=<slug>` returns the stored `ourCall`, `grandMedian`, and (when the model is running on stale sub-inputs) a top-level `caveat` string.
- The worker's `predictionSlugFor` regex is strict: NFP matches only "Non-Farm Employment Change" and "NFP" (not "ADP Non-Farm Employment Change"), FOMC matches only "Federal Funds Rate" / "FOMC Rate Statement" / "FOMC Statement" (not "FOMC Member X Speaks"). `seedBetaPlaceholders` self-corrects by deleting any future-dated `v1-beta` record whose slug no longer maps to a current event.

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

### 5. A live predictor must never anchor on hardcoded scalar inputs.

`final_report.py` originally pinned `CONSENSUS_NFP_K = 85.0` and `PREDICTION_MARKET_NFP_K = 82.0` at module scope. Those were the correct values for the July 2026 run cycle when the scaffold was written. When the cron fired for the September release, the same July numbers flowed into the Bayesian blend and the published prediction claimed "IN LINE WITH consensus" while the true deviation was +35K (real ForexFactory consensus was +55K, not +85K).

Every per-release scalar that feeds a live predictor must resolve at runtime from an env var or a live source, not from a module constant. In GHA context, a missing required env var is a hard error; refuse to publish. Local dev keeps a fallback with a `[warn]` line so `python run.py` still works offline.

When a required live source is not ready yet (like Kalshi tickers unverified for prediction markets), keep the hardcode but propagate an `is_stale` flag into the published payload's top-level `caveat` field so consumers see it. Never ship a "final" prediction without the caveat when it is anchored to partially-stale inputs.

Fixed in `4d7651f` (predictor repo) and matching worker changes in the web repo. Cost: a full corrective commit within one hour of the original ship.

### 6. Verify third-party API contracts before wiring them into the pipeline.

Two contract-shape assumptions bit us on 2026-09-02:

**Ticker mapping.** `KALSHI_SERIES.nfp` was configured as `["KXNFP", "KXNONFARMPAYROLL"]`. Neither exists in Kalshi's Economics category. The real series is `KXUSNFP` ("US nonfarm payrolls in [month]"). The `?kalshi-diag` endpoint added to the worker returned the actual `/series?category=Economics` list, which surfaced the correct ticker in seconds. Fix: name every third-party identifier you configure as a "guess, verify before ship" item and add a diag route that reveals the real values.

**Response semantics.** Kalshi NFP markets are binary contracts on ranges ("NFP > 60K" @ yes-price 0.7). The worker's `fetchKalshi` returns the yes-price formatted as a percentage string like `"5.4%"`. The predictor's blend expects a jobs-K central estimate. A percentage YES-price and a jobs-K point estimate are semantically different values that share no interpretable relationship. Wiring the current worker output straight into `NFP_PREDICTION_MARKET_K` would have produced garbage. Fix: at each pipeline boundary, write down what the sender's value means (units + interpretation) and what the receiver expects. Do not assume "market value" means the same thing on both ends.

For Phase 2, before adding any new external data source: (a) confirm the identifier resolves via a diag call; (b) inspect the response shape end to end; (c) document unit + semantics at every pipeline boundary; (d) unit-test the parse step against a captured real response, not against your assumption of the response.

## Non-blocking followups from Phase 1

Carry these into Phase 2 when convenient. None block the current pipeline.

- `fetch_calendar.py` gets `nextWeek: HTTP 404` from ForexFactory. `thisWeek` covers 7 days ahead including the next NFP, so predictions are not affected, but the fallback source URL is worth investigating.
- `run.py` was already threaded to accept `NFP_RELEASE_DATE` via env, but the BANNER string was hardcoded. Fixed for NFP. If Phase 2 adds CPI or FOMC live models, mirror the same env-driven pattern from the start.
- Phase 1.5 open item: teach the worker to compute an implied jobs-K central estimate from the Kalshi contract ladder, then change `predictionMarkets.value` output to jobs-K units (currently a YES-price percentage). Once that is done, add a workflow step that pulls `predictionMarkets.value` from the worker before `emit.py` runs and passes it as `NFP_PREDICTION_MARKET_K`. Then the caveat can be removed from the ourCall payload. Same ladder-to-central-estimate work will apply to Kalshi CPI and FOMC contracts in Phase 2.
- The `PredictionRecord.ourCall` TypeScript type in the worker does not include `caveat`. Cloudflare's JSON storage preserves the field via spread, so KV holds it, but strict-typed consumers on the reader side will not see it. Add `caveat` to the type when Phase 2 opens the worker for edits.

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
| 5 | predict-nfp 33621457578 | green in 66s, but published +90K anchored to stale July consensus | Rule 5 not yet enforced |
| 6 | predict-nfp 33624407092 | green in 70s, published corrected +80K with live +55K consensus | Rule 5 enforced (`4d7651f`); consensus wired from worker |

Total time from picking up the loose thread to a corrected live prediction: about 90 minutes of active work across seven commits (four predictor, three worker), plus one round of worker deploys.

## Worker-side changes shipped alongside Phase 1

The predictor repo cannot ship in isolation. These calendar-worker commits (in the FAR web repo) were required to close Phase 1:

- `95eeda8` tightened `predictionSlugFor` (excludes "ADP Non-Farm Employment Change" and "FOMC Member X Speaks"), added self-correcting placeholder cleanup, added `?kalshi-diag` endpoint.
- `3b5ee25` fixed Kalshi NFP series ticker (`KXNFP` -> `KXUSNFP`, verified via `?kalshi-diag`).
- One follow-up commit added `?markets-debug` for per-slug raw Kalshi + Polymarket inspection.

Every Phase 2 predictor scaffold should assume worker-side changes will be needed and coordinate the deploy sequence early.
