# Employment Cost Index prediction — target 2026-10-30 (T-56)

**Model version:** `v1-simple-blend`
**Published:** 2026-09-04T08:10:54.915835+00:00

## Final pick

**+0.9%** q/q Employment Cost Index (total civilian compensation)

- Regime: elevated wage growth
- 68% CI: [+0.79%, +0.99%]
- 95% CI: [+0.69%, +1.09%]
- Lean vs consensus: no consensus
- Sub-models used: anchor

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| consensus | — | 0.05pp |
| anchor | +0.89% | 0.10pp |

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of FF consensus + FRED
ECIALLCIV last-print persistence anchor.

## Positioning

The Fed's cleanest wage-inflation read. Captures wages + benefits and
avoids composition bias that plagues Average Hourly Earnings from NFP.
Quarterly release means each print carries outsized weight in the
policy signal. Runs hot (≥0.9pp q/q) → persistent-inflation risk;
cool (<0.6pp) → labor market softening.

## Change log

- **v1-simple-blend (2026-09-04)** — first ship.
