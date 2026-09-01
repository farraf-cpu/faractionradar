# NFP Predictor — Model Card

**Model version:** `v1-bayesian-blend`
**Event:** US Non-Farm Payrolls (monthly, first Friday, 08:30 ET)
**Output:** point estimate + 68%/95% CI, in thousands of jobs

## What this model does

Produces a single blended payroll forecast by averaging **seven** sub-models, weighted by each sub-model's historical Mean Absolute Error (MAE). Lower-MAE sub-models get more weight in the final blend. This "Bayesian blend" approach is more robust than any single model because different signals dominate in different regimes (post-COVID vs. pre-2020, high-JOLTS quits vs. low, etc.).

## The seven sub-models

| # | Sub-model | Signal source | Typical MAE | Notes |
|---|-----------|---------------|-------------|-------|
| 1 | Bloomberg consensus | Bloomberg survey median | ~55 K | Broad market consensus; overweight in normal months |
| 2 | Prediction markets (avg) | Kalshi + Polymarket average | ~40 K | Best single signal in recent regime |
| 3 | ML ensemble (revised) | ~34 FRED series + gradient boost | — | Trained on revised NFP prints |
| 4 | First-print ensemble | Same features, trained on first prints | — | Captures "revision drift" signal |
| 5 | Bridge models median | ADP + ISM + claims → NFP | — | Classic macro-bridge approach |
| 6 | Sector decomposition (11) | Employment by industry | — | Bottom-up rebuild across 11 sectors |
| 7 | Grand median (all models) | Median of the six above | — | Meta-model, dampens outliers |

Weights update monthly based on rolling 24-month MAE. Weights are visible in the report .md file for every prediction (`reports/YYYY-MM/nfp-t-N.md`).

## Data pipeline

**Refresh:** ~34 FRED series pulled at every run via `src/fred_fetch.py`. Committed to `data/raw/` so the feature matrix is reproducible from git history.

**Features:** `src/build_features.py` builds the feature matrix + applies manual overrides (currently none, but Vega/user can inject one via the module).

**Model orchestration:** `src/final_report.py` runs all seven sub-models sequentially, then blends. Output object matches the shape consumed by `emit.py`.

## Prediction cadence

5 runs per NFP print, keyed off the first-Friday release date:

| Run | When | Purpose |
|-----|------|---------|
| T-7 | previous Friday | Initial call, sets the anchor |
| T-4 | Monday | ADP releases, first update |
| T-3 | Tuesday | JOLTS releases, second update |
| T-2 | Wednesday | Continuing claims + ADP revisions |
| T-24h | Thursday | Final lock, all pre-print signals in |

Each run POSTs to the calendar-worker `/upload` endpoint AND commits its full `.md` report + a `predictions.jsonl` row back to this repo. The git ledger is the authoritative track record.

## Failure modes we know about

- **Manual override signal:** if the user overrides a feature (e.g., government shutdown quirks), we log the override and re-run. Overrides are visible in the .md report.
- **FRED outage:** the `fred_fetch` module warns and falls back to the last-committed CSV. Prediction still runs; report notes staleness.
- **Sub-model disagreement:** if the blend's CI widens dramatically, the report includes a "component disagreement" section flagging which sub-models are pulling apart. Reader can judge whether to trust the blend.

## What we're NOT claiming

- This is not a trading signal. It's a point estimate + confidence interval, published for transparency and to be scored against actuals over time.
- The 68% CI is empirically calibrated from historical error distributions, not a theoretical Gaussian.
- We are not the fastest signal (Bloomberg terminal is), nor the deepest (Fed staff internal models). We are the most **open** — every prediction, sub-model breakdown, and weight update is on-the-record in git.

## Scoring

Every prediction gets scored against the actual print. Cumulative accuracy vs. Bloomberg consensus is published monthly on faractionradar.com/calendar/archive. Target: OUR CALL closer to actual than Bloomberg on ≥50% of prints over rolling 12 months. Baseline: our local predictor's historical hit rate matches or exceeds this.

## Change log

- **v1-bayesian-blend (2026-09-01)** — initial version. 7 sub-models, MAE-weighted blend.
