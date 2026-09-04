# Phase 1.6 learnings — Tier 2 expansion (12 predictors)

Phase 1.6 shipped 2026-09-04 (~2h burst before NFP resolution). Scope:
12 new v1-simple-blend predictors bringing the registry from 29 → 41
live models. Coverage now spans all US top-tier + most Tier 2
economic releases.

Read this before adding a new predictor. It refines rules from Phase 1.

## What's live now (Phase 1.6 additions)

| Slug | Event | FRED anchor | Cron UTC |
|------|-------|-------------|----------|
| income | Personal Income m/m | PI (pch, 3-mo mean) | 16:20 |
| caputil | Capacity Utilization | TCU (level, 3-mo mean) | 16:25 |
| caseshiller | S&P/Case-Shiller 20-City HPI y/y | SPCS20RSA (pc1, 3-mo mean) | 16:30 |
| eci | Employment Cost Index q/q | ECIALLCIV (pch, last print) | 16:35 |
| factory | Factory Orders m/m | AMTMNO (pch, 3-mo mean) | 16:40 |
| construction | Construction Spending m/m | TTLCONS (pch, 3-mo mean) | 16:45 |
| adtrade | Advance Goods Trade Balance | BOPGTB (levels/1000, 3-mo mean) | 16:50 |
| businv | Business Inventories m/m | BUSINV (pch, 3-mo mean) | 16:55 |
| wholesale | Wholesale Inventories m/m | WHLSLRIMSA (pch, 3-mo mean) | 17:00 |
| credit | Consumer Credit m/m Change | TOTALSL (chg/1000, 3-mo mean) | 17:05 |
| imprices | Import Prices m/m | IR (pch, 3-mo mean) | 17:10 |
| budget | Federal Budget Balance | MTSDS133FMS (levels/1000, same-mo-yr-ago) | 17:15 |

**Worker-side FRED release IDs registered:** 199 (Case-Shiller), 11
(ECI), 95 (Factory — shared with Durable; filtered by day-of-month ≤ 15),
229 (Construction), 435 (AdvTrade), 25 (Business Inv), 290 (Wholesale),
14 (Consumer Credit), 188 (Import Prices), 363 (Monthly Treasury).

Two of these (Credit T-4, Budget T-7) fire naturally at 17:05 + 17:15 UTC
on the same day they were shipped (Sep 4). Smoke-verified via
workflow_dispatch on real target dates before natural cron.

## Rules learned

### Rule 6: parts_tbl label MUST match MAE dict key exactly

In `build_report_md`, the `parts_tbl` loop iterates over
`(("consensus", consensus), ("anchor", anchor))` (or `("trend", trend)`).
The labels used inside must be **exact string matches** for `MAE` dict
keys. Any parenthetical clarification like `"anchor (yr ago)"` breaks
`MAE[name]` lookup at report-render time. The failure only surfaces at
the FIRST real fire because smoke tests with missing sub-models hit the
soft-skip path earlier.

**Bit us:** Budget `emit_budget.py` had `"anchor (yr ago)"` in the tbl
loop but `MAE = {"consensus": 15.0, "anchor": 40.0}` in the dict.
KeyError blocked emit at report-build step (after successful blend
computation). Fix landed in commit `cb5cbb9`.

**How to apply:** When copying the emit_X.py template, keep the parts_tbl
labels literally equal to MAE keys. Put explanatory text (like "yr ago")
in the section HEADER above the table, not the row label. Grep to
verify: `grep 'for name, v in' emit_*.py` — every entry should use
labels that exist in the file's MAE dict.

### Rule 7: FRED release schedule reuse — filter, don't duplicate

Some FRED releases fire twice per cycle for different reports (M3
Survey release 95 = Factory Orders full report ~first week + Advance
Durable Goods ~last week). Don't fetch the release twice — fetch once
and filter by day-of-month in the worker's
refreshUpcomingMarquee loop.

Applied to Factory Orders: `factoryDates = m3Dates.filter((d) =>
Number(d.slice(-2)) <= 15)`. First-week entries only.

### Rule 8: Not everything popular is on FRED

Blockers hit during Phase 1.6:
- **NAR Pending Home Sales** (PHSI) — proprietary to NAR, not on FRED.
  Housing pipeline gap remains. Would need NAR direct scrape (paid) or
  a proxy from Existing Home Sales + Housing Starts pipeline lag.
- **S&P Global PMI Composite/Mfg/Svc** — proprietary to S&P Global, not
  on FRED. FF calendar includes these but no FRED anchor. Could ship a
  consensus-only predictor but Phase 2 accuracy would be limited.
- **NFIB Small Business Optimism** — proprietary to NFIB, not on FRED.

For any of these, if the user greenlights paid data, we can revisit.

### Rule 9: Same-month-last-year is better than 3-mo mean for seasonal series

Federal Budget Balance has strong quarterly seasonality (April tax-day
surplus, other months deficit). A 3-mo mean anchor smears seasonal
signal. Use `sort_order=desc&limit=13` and take the 12-months-ago
observation.

Applied to Budget: `fetch_fred_anchor()` in `emit_budget.py` reads
`obs[12]` (the 13th observation = 12 months back).

Consider same pattern for any series with clear seasonal pattern
(e.g. energy-heavy inventories, retail spending components).

## What's next

**Phase 2 upgrades — deferred:**
- CPI → Bayesian blend with Cleveland Fed nowcast + trimmed-mean CPI + shelter carve-out
- FOMC → outcome-distribution model with SEP + futures + speaker hawkishness
- NFP → additional sub-models (ADP correlation, weekly claims trend, sector-decomp refinement)
- Case-Shiller → FHFA cross-check + regional-city decomposition
- BusinessInv → inventory-to-sales ratio sub-model
- Budget → receipts vs outlays decomposition + tax-season seasonality model

**Bayesian pattern to standardize (post-Phase-2):** All v2 models should
share the same bayesian-blend infrastructure (inverse-variance weighting +
posterior CI + walk-forward MAE evaluation). Extract shared blend module
so v2 emits look uniform.

**Coverage gaps that remain (Tier 3+, low-priority):**
- Pending Home Sales, NFIB SBOI, S&P Global PMIs (all data-access blocked)
- Weekly EIA Petroleum data (weekly cadence, oil-market specific)
- TIC Long-Term Securities Purchases (Tier 3 macro-flow indicator)
- ISM sub-indices (Prices Paid, Employment) — part of parent ISM release

## Ledger of Phase 1.6 commits (chronological)

- `da9d61b` — Personal Income
- `c7c4921` — Capacity Utilization
- `3abe015` — S&P/Case-Shiller HPI
- `264ad7c` — Employment Cost Index
- `d8a4c3d` — Factory Orders
- `a05e7a2` — Construction Spending
- `0676e9b` — Advance Goods Trade Balance
- `f1bf512` — Business Inventories
- `2110107` — Wholesale Inventories
- `3bd0c62` — Consumer Credit
- `9b8fcaf` — Import Prices
- `0056c44` — Monthly Treasury Budget
- `cb5cbb9` — fix(budget): MAE key mismatch (Rule 6)

Worker-side companion commits in far-reach/faractionradar-web
(`calendar-worker/src/index.ts` history). Wrangler versions cited in
memory's session-resume file.
