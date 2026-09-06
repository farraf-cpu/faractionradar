# MX CPI Predictor - Model Card

**Model version:** `v1.1-inegi`
**Event:** MX INPC y/y (monthly, ~9th of following month, 12:00 UTC / 07:00 CDMX, INEGI)
**Status:** Live — cadence T-7, T-4, T-3, T-2, T-1 via `predict-mxcpi.yml`

## What v1.1-inegi does

Inverse-MAE-weighted blend of up to 2 sub-models:

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` → matched FF `forecast` field | ~0.15 |
| INEGI BIE INPC y/y 3-mo mean | inegi.org.mx/app/api/indicadores indicator 628194 (opt-in via `INEGI_TOKEN`) | ~0.25 |

FRED coverage is stale (`CPALTT01MXM659N` last obs 2025-03) — INEGI is
the authoritative Mexican statistics source. When `INEGI_TOKEN` is unset
on the farraf-cpu repo, trend sub-model soft-skips and predictor
degrades to consensus-only (v1 behavior). Same opt-in pattern as
KOSIS (KR), MOSPI (IN), ESTAT (EU).

## Positioning

Phase 13 MXN expansion. Banxico targets 3% CPI y/y with +/- 1pp band.
Released monthly by INEGI ~9th of following month at 06:00 CST (12:00
UTC winter).

Regime labels on the report:
- ≥ 5.0%: hot MX inflation (Banxico hawkish pressure)
- 4.0-5.0%: above Banxico target band
- 3.0-4.0%: upper half of band
- 2.0-3.0%: lower half of band
- < 2.0%: below Banxico target / disinflation

## Activate INEGI trend

1. Register free account at https://www.inegi.org.mx/app/api/indicadores/interfaz.html
2. Copy issued token
3. Set `INEGI_TOKEN` repo secret on farraf-cpu/faractionradar
4. Next scheduled run of predict-mxcpi.yml activates the trend anchor
   automatically

## Phase 2 candidates

- **INPC subyacente (core CPI)** — INEGI publishes core alongside
  headline; add as 3rd sub-model when core-vs-headline divergence
  matters for Banxico signal.
- **Banxico target-band cross-check** — regime annotation based on
  where the print lands vs 3% +/- 1pp band edges.

## Change log

- **v1.1-inegi (2026-09-06)** — added INEGI BIE INPC trend anchor
  (opt-in via `INEGI_TOKEN`). Same pattern as KOSIS/MOSPI/ESTAT. Also
  cleaned up copy-paste bugs in prior v1 (docstring/regime/report
  strings had stray JP/NZ/CH references).
- **v1-simple-blend (2026-09-05)** — first ship. Phase 13 MXN,
  consensus-only pending INEGI API integration.
