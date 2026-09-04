# Capacity Utilization prediction — target 2026-09-16 (T-12)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T07:48:23.171169+00:00

## Final pick

**76.2%** Capacity Utilization Rate

- Regime: healthy utilization
- 68% CI: [75.78%, 76.58%]
- 95% CI: [75.38%, 76.98%]
- Lean vs consensus: no consensus
- Sub-models used: anchor

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

- **v1-simple-blend (2026-09-04)** — first ship.
