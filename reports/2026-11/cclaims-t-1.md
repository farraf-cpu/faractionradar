# Continuing Claims prediction — target 2026-11-12 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-11T22:06:35.067514+00:00

## Final pick

**1709.50M** continuing unemployment claims (SA)

- Regime: elevated persistence
- 68% CI: [1709.47M, 1709.53M] · sigma source: prior (inverse-MAE)
- 95% CI: [1709.44M, 1709.56M]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 20K |
| trend | 1709.50M | 30K |

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
