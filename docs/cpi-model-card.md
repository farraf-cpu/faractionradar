# CPI Predictor — Model Card

**Model version:** `v1-beta` (placeholder — no trained model yet)
**Event:** US Consumer Price Index (monthly, mid-month, 08:30 ET)
**Status:** Beta — OUR CALL cell shows "model not yet trained · beta shipping Phase 2 (EUR expansion)"

## Why no model yet

Phase 1 scope is NFP only. CPI + FOMC ship with visible-roadmap placeholders so the /calendar page can launch with all four columns filled for NFP, and readers can see exactly which events we've built for vs. which are coming.

Building CPI right is non-trivial:
- Core vs. headline distinction, shelter revisions, energy volatility
- Post-COVID regime shift means shorter usable training window
- The Bayesian-blend architecture designed for NFP transfers, but sub-models change (no ADP-analog for CPI)

## What we DO show today

The calendar row for CPI events still populates three of the four columns:

- **Consensus** — from ForexFactory forecast field
- **Prediction Markets** — from Kalshi + Polymarket if a contract exists for that specific print
- **Grand Median** — currently null (no sub-models yet)
- **OUR CALL** — "model not yet trained · beta shipping Phase 2 (EUR expansion)"

## Phase 2 target

Ship a `v1-bayesian-blend` CPI predictor alongside the EUR expansion (ECB rate decisions, Eurozone CPI, DE IFO). Sub-models planned:

- Bloomberg consensus
- Prediction markets (Kalshi + Polymarket)
- Cleveland Fed nowcast
- Trimmed-mean CPI trend
- Energy/food carve-out
- Shelter component tracker
- Grand median

Rough MAE target: <0.10% on core CPI m/m.

## Change log

- **v1-beta (2026-09-01)** — placeholder shipped alongside NFP. No trained model.
