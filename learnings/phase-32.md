# Phase 32 — FOMC v2.1-kalshi-ladder

**Ships (2026-09-06):**
- `emit_fomc.py` — parses `FOMC_MARKET_LADDER` env (JSON list of
  `{threshold, probability}`), replaces normal-CDF outcome distribution
  with market-derived per-bucket probs when ladder is present.
- `.github/workflows/predict-fomc.yml` — extracts `ladder[]` from
  `/public/kalshi-implied` and exports as `FOMC_MARKET_LADDER` env.
  `MODEL_VERSION` bumped to `v2.1-kalshi-ladder`.
- `docs/fomc-model-card.md` — v2.1 rewrite.
- Worker `src/prediction-markets.ts` — `computeImpliedKFromKalshi`
  now propagates `ladder` through to callers.
- Worker `src/index.ts` — MODEL_REGISTRY FOMC entry updated;
  `/public/kalshi-implied` note documents ladder shape.

## Rules captured

- **Rule 40:** For discrete-outcome prediction markets (Fed target rate,
  which is quantized at 25bp), interpolating survival `P(rate > x)`
  between rungs LINEARLY implies smooth mass between rungs — which is
  false. Use a step-below function: `survival(x) = P(rate ≥ next_rung_up)`.
  Linear interpolation biases toward flat distributions; step function
  correctly assigns all mass to rung levels. Verified with synthetic
  ladders that recover the input pmf exactly (65% cut25 → cut25 bucket
  = 0.65 after normalization).
- **Rule 41:** F-string docstrings that contain curly braces in prose
  (e.g. `{hike50, hike25, hold}`) break the Python parser. Either
  double the braces (`{{hike50, hike25, hold}}`) or rewrite the prose
  without braces. Bit us mid-build 2026-09-06.

## Why this matters

FOMC outcome distribution is the primary consumer-facing artifact for
the rate-decision predictor. The Gaussian discretization approximated
the market's belief with N(point, sigma^2), but Kalshi's ladder IS the
market's per-outcome pricing directly — no need to approximate. This
should materially improve calibration for asymmetric cut/hike scenarios
where market pricing is not Gaussian.

## Smoke plan

Local smoke passed with three synthetic ladders (dovish, hawkish, hold-
dominated). Live smoke: fire `predict-fomc.yml` after worker deploy
lands the ladder in `/public/kalshi-implied`. Confirm output prediction
carries `outcomeDistribution.source == "kalshi-ladder"`.
