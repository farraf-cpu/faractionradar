# Durable Goods Orders prediction — target 2026-09-25 (T-0)

**Model version:** `v1.1-simple-blend`
**Published:** 2026-09-25T10:43:47.288122+00:00

## Final pick

**+0.1% m/m** (Durable Goods Orders, headline)

- 68% CI: [-0.28%, +0.43%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.63%, +0.78%]
- Lean vs consensus: above consensus by 0.4pp
- Sub-models used: consensus, trend, core_orders


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.50 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | -0.30% | 0.5 pp |
| trend | -0.78% | 0.8 pp |
| core_orders | +1.17% | 0.6 pp |

## Method

`v1.1-simple-blend`: inverse-MAE-weighted mean of up to 3 sub-models —
consensus (~0.5pp MAE) + FRED DGORDER 3-month trend (~0.8pp MAE) + FRED
NEWORDER 3-month core-orders trend (~0.6pp MAE, conservative pre-empirical).
Durable goods is one of the noisiest monthly prints — a single-plane
Boeing order can swing headline by 2pp+. Core capex orders (NEWORDER)
strips that transportation noise; historically correlates ~0.65 with
headline direction with materially lower variance.

Phase 2 target:
- **Core Durable Goods Orders split** — separate slug `durable-core-<date>`
  for the ex-transportation version. Core is what markets actually watch
  since it strips the Boeing/defense noise
- **Boeing 737 MAX orders tracker** — Boeing reports monthly commercial
  aircraft orders separately; subtract from headline to build a
  "durable ex-Boeing" leading indicator

## Change log

- **v1.1-simple-blend (2026-09-07)** — added FRED NEWORDER (Nondefense
  Capital Goods Excluding Aircraft) 3-mo trend as core-orders sub-model.
  MAE weight 0.6pp is conservative pre-empirical; empirical MAE auto-tune
  replaces prior weight once N>=5 resolutions.
- **v1-simple-blend** — first ship.
