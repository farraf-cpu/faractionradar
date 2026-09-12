# Capacity Utilization prediction — target 2026-09-16 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-12T16:31:47.259932+00:00

## Final pick

**76.2%** Capacity Utilization Rate

- Regime: healthy utilization
- 68% CI: [75.78%, 76.58%] · sigma source: prior (inverse-MAE)
- 95% CI: [75.38%, 76.98%]
- Lean vs consensus: no consensus
- Sub-models used: anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.40 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.20pp |
| anchor | 76.18% | 0.40pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED TCU
3-month mean anchor. Capacity Utilization is a slow-moving level series;
naive persistence (assume last-3-month mean) is a reasonable prior.

## Positioning

Fed G.17 release, published simultaneously with Industrial Production
(same day, same time). Cap Util measures actual-vs-sustainable-max output
across manufacturing + mining + utilities. Above ~80% signals inflationary
capacity pressure; below ~75% signals slack. Fed watches it as a
capacity-side inflation input alongside labor slack.

## Change log

- **v1-simple-blend (2026-09-12)** — first ship.
