# FOMC Predictor — Model Card

**Model version:** `v1-beta` (placeholder — no trained model yet)
**Event:** FOMC federal funds rate decision (~8 meetings/year)
**Status:** Beta — OUR CALL cell shows "model not yet trained · beta shipping Phase 2 (EUR expansion)"

## Why no model yet

Phase 1 scope is NFP only. FOMC + CPI ship with visible-roadmap placeholders. Fed rate decisions are a fundamentally different modeling problem from monthly data prints:

- **Discrete outcomes** (hold / cut 25 / cut 50 / hike 25 / hike 50) rather than a continuous point estimate
- **Fed speak** — SEP, dot plot, meeting minutes, Powell speeches all carry signal that's hard to featurize
- **Prediction markets are already excellent** here — Kalshi + Polymarket routinely lead Fed funds futures on rate calls

Our value-add for FOMC won't be a better probability — it'll be a **transparent decomposition** of what drives our probability (which speakers, which data prints, which market moves).

## What we DO show today

Same as CPI:

- **Consensus** — ForexFactory forecast (unusual for FOMC — often blank; falls back to market implied)
- **Prediction Markets** — Kalshi + Polymarket, which are the primary signal here
- **Grand Median** — currently null
- **OUR CALL** — "model not yet trained · beta shipping Phase 2 (EUR expansion)"

## Phase 2 target

Discrete-outcome Bayesian model with sub-models:

- Prediction markets (Kalshi + Polymarket average, weighted heavy)
- Fed funds futures implied probability
- SEP dot-plot median (from most recent SEP release)
- Speaker-hawkishness rolling index (Fed speeches since last meeting)
- Data surprise index (CPI + NFP + PCE surprises since last meeting)
- Grand median

Output: probability distribution over the 5 discrete outcomes above, plus the "point estimate" being the modal outcome. Report shows full distribution.

## Change log

- **v1-beta (2026-09-01)** — placeholder shipped alongside NFP. No trained model.
