# Continuing Claims prediction — target 2026-09-24 (T-1)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-23T15:39:09.698232+00:00

## Final pick

**1761.25M** continuing unemployment claims (SA)

- Regime: elevated persistence
- 68% CI: [1761.22M, 1761.28M] · sigma source: prior (inverse-MAE)
- 95% CI: [1761.19M, 1761.31M]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.03 K |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 20K |
| trend | 1761.25M | 30K |

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
