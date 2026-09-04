# Core PCE Predictor - Model Card

**Model version:** `v1.1-simple-blend`
**Event:** US Core PCE m/m (monthly, ~last business day, 08:30 ET, BEA; same release as headline PCE)
**Status:** Live - cadence T-7, T-4, T-3, T-2, T-1 + T-0 release-day refresh via `predict-corepce.yml`

## What v1.1-simple-blend does

Inverse-MAE-weighted blend of 3 sub-models. Cron 17:40 UTC daily +
10:30 UTC on release day.

| Sub-model | Source | Historical MAE (pp) |
|-----------|--------|---------------------|
| Bloomberg / FF consensus | live from calendar-worker `?read` | ~0.05 |
| **Cleveland Fed nowcast** | daily update from Cleveland Fed public JSON, 'Core PCE Inflation' series. Active during PCE cycle. Soft-skips during CPI cycle. | **~0.04** (tightest) |
| FRED PCEPILFE 6-mo mean m/m | Core PCE ex food + energy | ~0.10 |

Cleveland Fed at 0.04pp MAE is the tightest sub-model when active. During
CPI cycle, blend falls back to consensus + trend only.

Value format: `+0.3%` m/m.

## Positioning

**Core PCE is the Fed's PRIMARY inflation target** — the specific number
they aim at when quoting the 2% goal. Tighter historical MAE than Core CPI
because analysts scrutinize it more heavily. Prints >0.3% m/m sustain
hawkish pressure; <0.2% opens easing path.

Same 3 sub-models as headline PCE predictor, applied to Core PCE series
(PCEPILFE for FRED trend, 'Core PCE Inflation' for Cleveland Fed).

## Cleveland Fed nowcast behavior

Cleveland Fed alternates between CPI + PCE nowcast cycles. Currently in
PCE cycle (leading to Sep 22 print). Core PCE Inflation series has
current values that our sub-model consumes. When CPI cycle activates
(~T-14 before each CPI release), Core PCE series returns empty and our
sub-model soft-skips.

## What v1.1 does NOT do (yet)

- **No sticky/flexible price decomposition** — sticky-price PCE
  moves slower than flexible; decomposing would give the Fed-relevant
  underlying trend more directly.
- **No shelter carve-out** — owner's-equivalent-rent is a big Core PCE
  component with own release cycle + lag structure.
- **No trimmed-mean cross-check** — Dallas Fed publishes trimmed-mean
  PCE (separate from trimmed CPI) that would be a reasonable additional
  sub-model.

## Change log

- **v1.1-simple-blend (2026-09-04)** — first ship with Cleveland Fed
  nowcast + consensus + FRED trend (3 sub-models).
