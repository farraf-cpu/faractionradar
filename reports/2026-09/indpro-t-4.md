# Industrial Production prediction — target 2026-09-16 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-12T15:44:29.693339+00:00

## Final pick

**+0.2% m/m** (Industrial Production Index, SA)

- 68% CI: [-0.25%, +0.55%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.65%, +0.95%]
- Lean vs consensus: no consensus
- Sub-models used: trend


## Empirical accuracy (live)

| Metric | Value |
|--------|-------|
| Prior MAE claim | 0.40 pp |
| Resolved predictions | 0 (first resolution pending) |
| Empirical MAE | — |
| Hit rate (ourCall closest) | — |

Empirical MAE + hit-rate auto-populate as predictions resolve. Once
count >= 5 the CI sigma will switch from the prior to the
empirical value.


## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.3 pp |
| trend | +0.15% | 0.4 pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus (~0.3pp) + FRED
INDPRO 3-mo trend (~0.4pp). Physical output measure — direct read on
manufacturing sector activity.

## Phase 2 targets

- **Capacity Utilization companion** — TCU (Total Capacity Utilization)
  releases same day; separate slug `capacity-<date>`
- **Manufacturing sub-index** — IPMANSICS (Mfg only) strips out utilities
  weather noise; helps on stormy months
- **Auto production tracker** — auto plant shutdowns/reopens drive 30%+
  of monthly Mfg variance; Ward's Intelligence has weekly data

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 21st event covered.
