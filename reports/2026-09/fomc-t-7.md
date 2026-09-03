# FOMC prediction — target 2026-09-17 (T-7)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-03T00:45:45.516574+00:00

## Final pick

**3.96%** target fed funds rate

- 68% CI: [3.90%, 4.02%]
- 95% CI: [3.84%, 4.08%]
- Direction: +21bp move vs current expected
- Sub-models used: market, anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| market | 4.00% | 0.05 pp |
| consensus | — | 0.07 pp |
| anchor | 3.75% | 0.25 pp |

## Method

v1-simple-blend: inverse-MAE-weighted mean of the sub-models above. Markets
carry ~10x the weight of the current-rate anchor because prediction markets
have historically led Fed rate calls. Phase 2 target is a proper discrete-
outcome model (probability distribution over hold / cut25 / cut50 / hike25)
using fed funds futures + SEP dot-plot + speaker-hawkishness index.

Point estimate is a scalar rate (e.g. "4.25%") not a discrete outcome.
That's a simplification — the true prediction is a distribution over
outcomes. Phase 2 will publish the full distribution.
