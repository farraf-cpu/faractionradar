# Industrial Production prediction — target 2026-11-17 (T-4)

**Model version:** `v1-simple-blend`
**Published:** 2026-11-13T21:35:52.764071+00:00

## Final pick

**+0.3% m/m** (Industrial Production Index, SA)

- 68% CI: [-0.08%, +0.72%] · sigma source: prior (inverse-MAE)
- 95% CI: [-0.48%, +1.12%]
- Lean vs consensus: no consensus
- Sub-models used: trend

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.3 pp |
| trend | +0.32% | 0.4 pp |

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
