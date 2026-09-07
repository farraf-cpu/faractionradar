# Backtest harness — Phase 2 v1

Replays FRED-based sub-models through recent history to produce
empirical MAE tables per sub-model. Enables replacing pre-empirical
starting-point MAE weights with values fit from actual data.

## Scope

**In scope for v1:**
- FRED-based sub-models on the 8 US predictors upgraded 2026-09-07
  (Retail, Housing, Confidence, Durable, Existing, NewHome, Core PPI, UMich).
- Rolling replay across the most recent 24 release dates per event.
- Point-in-time discipline: at each replay date, only use FRED
  observations dated ≤ that date.

**Explicitly out of scope for v1:**
- Consensus sub-model backtesting — FF forecast history is not
  publicly archived, so we can't reconstruct consensus at T-N days
  before a historical release.
- Kalshi ladder / market sub-model backtesting — Kalshi does not
  expose historical ladder snapshots; only the current live ladder.
- Vintage-honest revision handling — FRED gives us the current
  (revised) series, not the first-print vintage. ALFRED (Archival
  FRED) supports this but our v1 harness accepts the drift and
  documents the caveat.
- Empirical MAE auto-tune coefficient refit — this harness produces
  MAE tables; the coefficient replacement is a follow-up step gated
  on user review of results.

## What this outputs

For each backtested predictor:

```
| release_date | v1_pred | v1.1_pred | actual | v1_err | v1.1_err |
|--------------|---------|-----------|--------|--------|----------|
| 2024-09-16   | +0.4%   | +0.35%    | +0.2%  | +0.2   | +0.15    |
| 2024-08-15   | ...     | ...       | ...    | ...    | ...      |
```

Aggregate summary:

```
Retail (n=24 recent releases):
  v1  (trend only)         MAE: 0.42pp   RMSE: 0.51pp
  v1.1 (trend + auto)      MAE: 0.38pp   RMSE: 0.47pp
  Improvement: 0.04pp (9.5% MAE reduction)
```

## Honest caveats

1. **Revision drift.** Current FRED values may differ from first-print.
   Backtest MAE is optimistic relative to what live trading would have
   seen. Fix requires ALFRED integration.
2. **Consensus omission.** v1 baseline here is "trend only" (no
   consensus). Live v1.1 uses trend + consensus + new sub-model.
   Backtest measures the FRED-side sub-model contribution only.
3. **Coefficient tuning is separate.** This harness measures the
   default coefficients we shipped 2026-09-07. Refit is a follow-up
   pass once we've reviewed these baseline numbers.
4. **Point-in-time cutoff is target's obs date (not release date).**
   FRED obs dates use the START of the covered month; releases happen
   1-4 weeks later depending on series. Using the target's obs date
   as cutoff strictly excludes the target AND all future obs — no
   future-peek. It also excludes same-month auxiliary series (e.g.
   TOTALSA that publishes ~5 days after month-end and IS available
   at retail's mid-month release), so the backtest is CONSERVATIVE
   on v1.1 auxiliary sub-models. Live v1.1 accuracy is expected to
   be at least as good as backtest v1.1 accuracy. Direction of the
   v1 → v1.1 improvement measurement is preserved.

## How to run

```bash
# Locally (requires FRED_API_KEY env)
python backtest/run_backtests.py --event retail --n 24

# All events
python backtest/run_backtests.py --all --n 24

# Via GHA workflow_dispatch
# Actions → "Backtest Harness" → Run workflow → pick event(s) + N
```

Outputs land in `backtest/results/<event>-YYYY-MM-DD.md` locally, or
as workflow artifacts on GHA.

## Next steps (Phase 2b, gated on user review of v1 results)

- ALFRED vintage integration (kill revision drift caveat)
- Coefficient sensitivity sweep (test OIL_SHOCK_COEFF ∈ [-0.6, -0.2],
  MORTGAGE_SENSITIVITY ∈ [-0.010, -0.003], etc.)
- Auto-refit: replace prior MAE weights with backtested values in
  each `emit_*.py` MAE dict + coefficient
- Consensus proxy via lagged mean (rough approximation)
