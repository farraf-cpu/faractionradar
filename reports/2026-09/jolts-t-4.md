# JOLTS Job Openings prediction — target 2026-09-08 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T15:14:22.525758+00:00

## Final pick

**7.33M** job openings (level, SA)

- Regime: moderating labor demand
- 68% CI: [7.08M, 7.58M]
- 95% CI: [6.83M, 7.83M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 150K |
| trend | 7.33M | 250K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~150K MAE) +
FRED JTSJOL 3-month trend (~250K MAE). Short trend window because JOLTS
has been volatile since 2022 (multiple months of 500K+ revisions).

## Why the Fed watches this

Openings/Unemployed ratio (JOLTS Job Openings / U-3 unemployment level) is
Fed Chair Powell's preferred labor-tightness gauge. Ratio >1.5 = extremely
tight; ratio ~1.0 = balanced; ratio <0.8 = slack. Our regime labels use
the openings level directly since the ratio requires waiting for NFP too.

Phase 2 target:
- **Openings/Unemployed ratio** — cross-fetch NFP unemployment level from
  KV, publish ratio alongside headline as a Fed-decision-relevant metric
- **Quits Rate sub-model** — JTSQUL (Quits Level) leads Openings by ~1
  month; add as sub-model
- **Hires vs Separations gap** — JTSHIL - JTSTSL is net employment
  addition; add as sanity check on Openings trend
