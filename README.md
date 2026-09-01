# FAR Predictors

Open-source Bayesian-blend predictors for high-impact macro events. Powers the OUR CALL column on [faractionradar.com/calendar](https://faractionradar.com/calendar).

## What this repo does

Every prediction the FAR Calendar publishes gets generated here and committed to git — so the full model output for every historical call is auditable forever. Anyone can:

- Read the model code (all here)
- Read the full report for any past prediction (`reports/YYYY-MM/*.md`)
- Read the raw prediction ledger (`predictions.jsonl`, appended by every workflow run)
- Fork the repo and run their own version

Nobody can fork the track record. That's the point.

## Predictors shipped

| Event | Model | Status | First shipped |
|-------|-------|--------|---------------|
| US Nonfarm Payrolls (NFP) | Bayesian-blend, 7 sub-models weighted by historical MAE | live | Phase 1 |
| US CPI | placeholder (beta shipping Phase 2) | placeholder | — |
| US FOMC rate decision | placeholder (beta shipping Phase 2) | placeholder | — |

## How runs happen

Automated via GitHub Actions on a schedule keyed to each event's release date. For NFP: 5 runs per print (T-7, T-4, T-3, T-2, T-24h days ahead). Each run:

1. Refreshes ~34 FRED series (raw data updated in `data/raw/`)
2. Rebuilds the feature matrix
3. Runs all 7 sub-models + Bayesian blend
4. POSTs the result to the calendar-worker `/upload` endpoint
5. Commits the full `.md` report to `reports/YYYY-MM/` and appends a row to `predictions.jsonl`

Total GHA cost: ~60 minutes/year for NFP. Public repo, unlimited free minutes.

## Local dev

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Local run (prints report to stdout, does not POST or commit)
python run.py

# Skip FRED refresh if you've run it recently
python run.py --no-refresh
```

You'll need a `FRED_API_KEY` env var (free from https://fred.stlouisfed.org/docs/api/api_key.html).

## Secrets (GHA)

Set in GitHub → Settings → Secrets and variables → Actions:

- `FRED_API_KEY` — from fred.stlouisfed.org
- `UPLOAD_AUTH_KEY` — shared with the calendar-worker; used to POST predictions

## Model methodology

See `docs/nfp-model-card.md` (todo) for the full breakdown of each sub-model's inputs, historical MAE, and blending weights.

## License

MIT — see `LICENSE`.
