# Capacity Utilization prediction — target 2026-10-16 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-12T23:04:54.618015+00:00

## Final pick

**76.4%** Capacity Utilization Rate

- Regime: healthy utilization
- 68% CI: [76.24%, 76.62%] · sigma source: prior (inverse-MAE)
- 95% CI: [76.05%, 76.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.20 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 76.50% | 0.20pp |
| anchor | 76.28% | 0.40pp |

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

- **v1-simple-blend (2026-10-12)** — first ship.
