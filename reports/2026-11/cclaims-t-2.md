# Continuing Claims prediction — target 2026-11-26 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-24T23:59:55.941762+00:00

## Final pick

**1717.00M** continuing unemployment claims (SA)

- Regime: elevated persistence
- 68% CI: [1716.97M, 1717.03M] · sigma source: prior (inverse-MAE)
- 95% CI: [1716.94M, 1717.06M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 20K |
| trend | 1717.00M | 30K |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~20K) + FRED
CCSA 4-week trend (~30K). Weekly cadence like Initial Claims.

## Relationship to Initial Claims

Continuing = pool of people still on benefits after initial filing.
Rising Continuing alongside flat Initial usually means hiring has slowed
(people can't find new jobs after being laid off). Directional cross-check
for the labor-market interpretation of Initial Claims.

## Phase 2 targets

- **Initial Claims spread** — Continuing / Initial ratio; ratio rising =
  hiring softening
- **Insured Unemployment Rate** — Continuing / Covered Employment; direct
  labor-slack metric

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 20th event covered.
