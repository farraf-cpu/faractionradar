"""Unit tests for backtest/harness.py — the pure logic, no network.

Verifies:
- slice_at_date correctly filters obs list
- mom_pct_from_levels computes m/m from levels list
- obs_to_floats extracts numeric values, skips "."
- BacktestSummary.from_errors computes MAE/RMSE/bias correctly
- format_report renders without crashing on empty + populated inputs
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# Allow `python tests/test_harness.py` from repo root
sys.path.insert(0, str(Path(__file__).parent))

from harness import (
    BacktestRow,
    BacktestSummary,
    format_report,
    mom_pct_from_levels,
    obs_to_floats,
    slice_at_date,
)


class TestSliceAtDate(unittest.TestCase):
    def test_strict_less_than(self):
        obs = [
            {"date": "2024-09-01", "value": "310.0"},
            {"date": "2024-08-01", "value": "309.5"},
            {"date": "2024-07-01", "value": "308.2"},
        ]
        # cutoff on the exact date of an obs — that obs is excluded
        result = slice_at_date(obs, "2024-09-01")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["date"], "2024-08-01")

    def test_cutoff_after_all(self):
        obs = [
            {"date": "2024-09-01", "value": "310.0"},
            {"date": "2024-08-01", "value": "309.5"},
        ]
        # cutoff far in the future — nothing filtered
        result = slice_at_date(obs, "2099-01-01")
        self.assertEqual(len(result), 2)

    def test_cutoff_before_all(self):
        obs = [
            {"date": "2024-09-01", "value": "310.0"},
        ]
        # cutoff before the earliest obs — everything filtered
        result = slice_at_date(obs, "2020-01-01")
        self.assertEqual(len(result), 0)


class TestMomPct(unittest.TestCase):
    def test_basic(self):
        levels = [110.0, 100.0, 90.0]
        result = mom_pct_from_levels(levels)
        # levels[0]/levels[1] = 10% up; levels[1]/levels[2] = 11.11% up
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result[0], 10.0, places=4)
        self.assertAlmostEqual(result[1], 11.1111, places=3)

    def test_zero_prev(self):
        # Division-by-zero guard: entries with prev==0 get skipped
        levels = [50.0, 0.0, 40.0]
        result = mom_pct_from_levels(levels)
        # First pair (50, 0) skipped; second pair (0, 40) still included
        # because we check `prev` which is levels[i+1] — here levels[1]=0
        # for the first pair (i=0), so first is skipped. levels[2]=40 for
        # second pair (i=1). 0-40 relative to 40 = -100%.
        self.assertEqual(len(result), 1)
        self.assertAlmostEqual(result[0], -100.0, places=4)


class TestObsToFloats(unittest.TestCase):
    def test_skips_dot(self):
        obs = [
            {"date": "2024-09-01", "value": "310.5"},
            {"date": "2024-08-01", "value": "."},  # FRED "no data" marker
            {"date": "2024-07-01", "value": "308.2"},
        ]
        result = obs_to_floats(obs)
        self.assertEqual(result, [310.5, 308.2])

    def test_handles_string_ints(self):
        obs = [{"date": "2024-01-01", "value": "100"}]
        result = obs_to_floats(obs)
        self.assertEqual(result, [100.0])


class TestBacktestSummary(unittest.TestCase):
    def test_from_errors_basic(self):
        errors = [1.0, -2.0, 3.0, -1.0]
        s = BacktestSummary.from_errors("test", errors)
        self.assertEqual(s.n, 4)
        self.assertEqual(s.n_valid, 4)
        # MAE = (1 + 2 + 3 + 1) / 4 = 1.75
        self.assertAlmostEqual(s.mae, 1.75)
        # bias = (1 - 2 + 3 - 1) / 4 = 0.25
        self.assertAlmostEqual(s.bias, 0.25)

    def test_from_errors_with_nones(self):
        errors = [1.0, None, 3.0, None]
        s = BacktestSummary.from_errors("test", errors)
        self.assertEqual(s.n, 4)
        self.assertEqual(s.n_valid, 2)
        # MAE over the 2 valid: (1 + 3) / 2 = 2.0
        self.assertAlmostEqual(s.mae, 2.0)

    def test_from_errors_all_none(self):
        s = BacktestSummary.from_errors("test", [None, None])
        self.assertEqual(s.n_valid, 0)
        self.assertIsNone(s.mae)
        self.assertIsNone(s.rmse)


class TestBacktestRow(unittest.TestCase):
    def test_error_auto_computed(self):
        r = BacktestRow(
            release_date="2024-09-15",
            v1_pred=0.4,
            v1_1_pred=0.35,
            actual=0.2,
        )
        self.assertAlmostEqual(r.v1_err, 0.2, places=4)
        self.assertAlmostEqual(r.v1_1_err, 0.15, places=4)

    def test_none_actual_leaves_error_none(self):
        r = BacktestRow(
            release_date="2024-09-15",
            v1_pred=0.4,
            v1_1_pred=0.35,
            actual=None,
        )
        self.assertIsNone(r.v1_err)
        self.assertIsNone(r.v1_1_err)


class TestFormatReport(unittest.TestCase):
    def test_empty_rows(self):
        # Should not crash on empty
        report = format_report("Test Event", [], [])
        self.assertIn("Test Event", report)
        self.assertIn("Releases replayed:** 0", report)

    def test_populated(self):
        rows = [
            BacktestRow(
                release_date="2024-09-15",
                v1_pred=0.4, v1_1_pred=0.35, actual=0.2),
        ]
        v1 = BacktestSummary.from_errors("v1", [r.v1_err for r in rows])
        v11 = BacktestSummary.from_errors("v1.1", [r.v1_1_err for r in rows])
        report = format_report("Retail", rows, [v1, v11])
        self.assertIn("Retail", report)
        self.assertIn("2024-09-15", report)
        # v1.1 has smaller error → should show reduction
        self.assertIn("reduction", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
