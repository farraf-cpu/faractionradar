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

**118 predictors across 25 currency areas.** All self-calibrating — each report
fetches empirical MAE + hit-rate from the calendar-worker at run time and,
once the resolved count reaches 5, auto-switches its CI sigma from the
prior to the empirical value.

Highlights:

| Event | Model | Notes |
|-------|-------|-------|
| US NFP | `v1.1-bayesian-blend-ladder-dist` | 7 sub-models + Kalshi KXUSNFP ladder → 6-bucket outcome distribution |
| US CPI | `v1.3-kalshi-ladder-dist` | consensus + Cleveland Fed nowcast + Kalshi KXCPI ladder + FRED trimmed-mean + FRED trend |
| US FOMC | `v2.1-kalshi-ladder` | Kalshi FED-DECISION ladder → market-derived per-outcome distribution; Gaussian fallback |
| 46 US 3-star events | v1-simple-blend | PPI/PCE/Retail/ISM/Claims/Housing/GDP + 34 more |
| 25 currency areas | rate + CPI + GDP predictors | ECB / BOE / BOJ / BOC / RBA / RBNZ / SNB / BOK / PBOC / MNB / CNB / NBP / BCB / Banxico / SARB / CBRT / RBI / Riksbank / Norges / BCCH / BI / BOI / NB / CBI |

`docs/*-model-card.md` has the full breakdown per predictor.

## How runs happen

Automated via GitHub Actions on a schedule keyed to each event's release
date. Marquee US events run 5 times per print (T-7, T-4, T-3, T-2, T-1);
smaller / quarterly / weekly events on their own natural cadence.

Each run:

1. Fetches per-event live inputs (FF consensus + Kalshi implied + FRED trend + native CB API when available)
2. Runs the inverse-MAE-weighted blend (or bayesian blend for NFP)
3. Fetches empirical MAE from calendar-worker `/public/models` for
   sigma auto-tune (dormant until N>=5)
4. POSTs the result to the calendar-worker `/upload` endpoint
5. Commits a full `.md` report to `reports/YYYY-MM/` and appends a
   row to `predictions.jsonl`

Total GHA cost: ~4000 minutes/year across all predictors. Public repo,
unlimited free minutes.

## Testing

Four regression suites run on every push + PR (see `.github/workflows/test.yml`):

- `test_ladder_distribution.py` — pins the ladder math + bucket variants + sigma auto-tune threshold
- `test_all_emitters_have_mae.py` — verifies every emit_*.py wires empirical MAE; rate-decisions wire outcome_dist
- `test_all_emitters_render.py` — smoke-renders every predictor's `build_report_md` against fake args
- `test_fleet_consistency.py` — every emitter has matching card + workflow + gate; workflows use `.python-version`; predict-*.yml has concurrency + git retry patterns

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

Per-predictor model cards live in `docs/*-model-card.md`. Shared helpers
(empirical-MAE fetch, sigma auto-tune, Kalshi ladder parsing, Gaussian
outcome-distribution discretization) live in `mae_utils.py`.

## License

MIT — see `LICENSE`.
