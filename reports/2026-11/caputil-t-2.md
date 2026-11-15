# Capacity Utilization prediction — target 2026-11-17 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-15T21:06:47.725601+00:00

## Final pick

**76.7%** Capacity Utilization Rate

- Regime: healthy utilization
- 68% CI: [76.53%, 76.91%] · sigma source: prior (inverse-MAE)
- 95% CI: [76.35%, 77.10%]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 76.80% | 0.20pp |
| anchor | 76.57% | 0.40pp |

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

- **v1-simple-blend (2026-11-15)** — first ship.
