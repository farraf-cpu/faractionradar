# ISM Manufacturing PMI prediction — target 2026-10-01 (T-2)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-29T14:36:29.992277+00:00

## Final pick

**54.7** (diffusion index; 50 = expansion threshold)

- Regime: modest expansion
- 68% CI: [53.7, 55.8] · sigma source: prior (inverse-MAE)
- 95% CI: [52.7, 56.8]
- Lean vs consensus: in line with consensus
- Sub-models used: consensus, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | 54.8 | 1.0 pts |
| anchor | 54.6 | 2.5 pts |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + optional
last-known-value anchor. ISM PMI is NOT on FRED (proprietary to Institute
for Supply Management) so no persistence trend sub-model in v1.

Phase 2 target adds regional Fed nowcasts as a leading-indicator sub-model:
Empire State (NY Fed), Philly Fed, Dallas Fed, Kansas City Fed, Richmond
Fed. All publish current-activity diffusion indexes 5-10 days ahead of ISM.
FRB Cleveland shows the aggregate of these regional indices lag ISM by
0.85 correlation — a proper weighted-average sub-model would tighten our
MAE from ~1.0 to ~0.7 index points.
