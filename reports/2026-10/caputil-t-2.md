# Capacity Utilization prediction — target 2026-10-16 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-10-14T20:15:42.594561+00:00

## Final pick

**76.4%** Capacity Utilization Rate

- Regime: healthy utilization
- 68% CI: [76.24%, 76.62%] · sigma source: prior (inverse-MAE)
- 95% CI: [76.05%, 76.80%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor

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

- **v1-simple-blend (2026-10-14)** — first ship.
