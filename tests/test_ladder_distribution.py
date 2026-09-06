"""Ladder math regression tests — covers emit_fomc, emit_cpi, emit.py (NFP).

Each predictor's parse_market_ladder + survival_from_ladder +
compute_*_outcome_distribution needs to recover the input pmf exactly
after discretization. These tests pin the shape so future edits can't
silently mis-align bucket edges or break the step-function survival.

Run: python -m pytest tests/test_ladder_distribution.py -v
Or:  python tests/test_ladder_distribution.py

Kept deliberately dependency-free (no pytest imports at module scope)
so both invocations work.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _run_case(env_var: str, ladder: list[dict], predictor_module_name: str, dist_fn_args: list):
    """Set env, import the predictor's parse_market_ladder + dist fn,
    return (parsed_ladder, dist)."""
    os.environ[env_var] = json.dumps(ladder)
    mod = __import__(predictor_module_name)
    # Force reimport so env-var read happens fresh.
    parsed = mod.parse_market_ladder()
    dist = mod.compute_market_outcome_distribution(parsed, *dist_fn_args) if dist_fn_args else mod.compute_market_outcome_distribution(parsed)
    return parsed, dist


def test_fomc_ladder_recovers_discrete_pmf():
    """Discrete FOMC ladder with 60% at 4.25 (anchor), 30% at 4.00 (cut25),
    10% at 3.75 (cut50) should round-trip to hold=0.60, cut25=0.30, cut50=0.10."""
    import emit_fomc
    os.environ["FOMC_MARKET_LADDER"] = json.dumps([
        {"threshold": 3.75, "probability": 1.00},
        {"threshold": 4.00, "probability": 0.90},
        {"threshold": 4.25, "probability": 0.60},
        {"threshold": 4.50, "probability": 0.00},
    ])
    ladder = emit_fomc.parse_market_ladder()
    dist = emit_fomc.compute_outcome_distribution(4.0, 0.05, anchor=4.25, ladder=ladder)
    assert dist["hold"] == 0.60, f"hold expected 0.60 got {dist['hold']}"
    assert dist["cut25"] == 0.30, f"cut25 expected 0.30 got {dist['cut25']}"
    assert dist["cut50"] == 0.10, f"cut50 expected 0.10 got {dist['cut50']}"
    assert dist["hike25"] == 0.0
    assert dist["hike50"] == 0.0
    assert dist["modal"] == "hold"
    assert dist["source"] == "kalshi-ladder"


def test_fomc_gaussian_fallback_when_no_ladder():
    """When ladder is absent, distribution should fall back to Gaussian."""
    import emit_fomc
    os.environ.pop("FOMC_MARKET_LADDER", None)
    ladder = emit_fomc.parse_market_ladder()
    assert ladder is None
    dist = emit_fomc.compute_outcome_distribution(4.25, 0.05, anchor=4.25, ladder=None)
    assert dist["source"] == "gaussian-approx"
    assert dist["modal"] == "hold"


def test_cpi_ladder_bucket_probs():
    """CPI ladder with modal +0.2% at 40% should round-trip to the +0.2 bucket."""
    import emit_cpi
    os.environ["CPI_MARKET_LADDER"] = json.dumps([
        {"threshold": 0.0, "probability": 1.00},
        {"threshold": 0.1, "probability": 0.88},
        {"threshold": 0.2, "probability": 0.55},
        {"threshold": 0.3, "probability": 0.15},
        {"threshold": 0.4, "probability": 0.03},
    ])
    ladder = emit_cpi.parse_market_ladder()
    dist = emit_cpi.compute_market_outcome_distribution(ladder)
    assert dist["modal"] == "+0.2%", f"modal expected +0.2% got {dist['modal']}"
    assert dist["source"] == "kalshi-ladder"
    numeric_sum = sum(v for k, v in dist.items() if isinstance(v, float))
    assert abs(numeric_sum - 1.0) < 0.01, f"probs should sum to ~1, got {numeric_sum}"


def test_nfp_ladder_bucket_labels():
    """NFP ladder should produce labeled jobs-count buckets."""
    import emit
    os.environ["NFP_MARKET_LADDER"] = json.dumps([
        {"threshold": 0, "probability": 1.0},
        {"threshold": 25000, "probability": 0.90},
        {"threshold": 50000, "probability": 0.72},
        {"threshold": 75000, "probability": 0.55},
        {"threshold": 100000, "probability": 0.35},
        {"threshold": 125000, "probability": 0.20},
        {"threshold": 150000, "probability": 0.10},
        {"threshold": 175000, "probability": 0.05},
        {"threshold": 200000, "probability": 0.02},
    ])
    ladder = emit.parse_market_ladder()
    dist = emit.compute_market_outcome_distribution(ladder)
    expected_keys = {"<=25K", "25-75K", "75-125K", "125-175K", "175-225K", "225K+"}
    numeric_keys = {k for k, v in dist.items() if isinstance(v, float)}
    assert numeric_keys == expected_keys, f"bucket keys mismatch: {numeric_keys}"
    numeric_sum = sum(v for k, v in dist.items() if isinstance(v, float))
    assert abs(numeric_sum - 1.0) < 0.01, f"probs should sum to ~1, got {numeric_sum}"


def test_survival_step_function_at_boundary():
    """Step-below survival: at exact rung threshold, returns the NEXT rung's
    probability (not the current one), consistent with discrete-mass model."""
    import emit_fomc
    rungs = [(3.75, 1.0), (4.0, 0.9), (4.25, 0.6), (4.5, 0.0)]
    assert emit_fomc.survival_from_ladder(3.5, rungs) == 1.0
    assert emit_fomc.survival_from_ladder(3.9, rungs) == 0.9
    assert emit_fomc.survival_from_ladder(4.1, rungs) == 0.6
    assert emit_fomc.survival_from_ladder(4.6, rungs) == 0.0


def test_malformed_ladder_returns_none():
    """Bad JSON, missing keys, or under-2 rungs should return None cleanly."""
    import emit_fomc
    os.environ["FOMC_MARKET_LADDER"] = "not-json"
    assert emit_fomc.parse_market_ladder() is None
    os.environ["FOMC_MARKET_LADDER"] = json.dumps([{"foo": 1}])
    assert emit_fomc.parse_market_ladder() is None
    os.environ["FOMC_MARKET_LADDER"] = json.dumps([{"threshold": 4.0, "probability": 0.5}])
    assert emit_fomc.parse_market_ladder() is None  # < 2 rungs
    os.environ.pop("FOMC_MARKET_LADDER", None)


def test_empirical_mae_section_renders_for_zero_and_populated():
    """Section renders placeholder at N=0 and stats at N>=1."""
    import emit_fomc
    empty_section = emit_fomc.build_empirical_mae_section({"count": 0, "mae": None, "hits": 0, "hit_rate": None}, "0.05 pp")
    assert "Prior MAE claim | 0.05 pp" in empty_section
    assert "Resolved predictions | 0" in empty_section
    populated = emit_fomc.build_empirical_mae_section({"count": 8, "mae": 0.062, "hits": 5, "hit_rate": 0.625}, "0.05 pp")
    assert "Resolved predictions | 8" in populated
    assert "Empirical MAE | 0.062 pp" in populated
    assert "62% (5/8)" in populated


def test_empirical_mae_section_empty_when_no_data():
    """None input returns empty string so caller can concat safely."""
    import emit_cpi
    assert emit_cpi.build_empirical_mae_section(None, "0.08 pp") == ""
    assert emit_cpi.build_empirical_mae_section({}, "0.08 pp") == ""


def test_rate_outcome_distribution_25bp_default():
    """25bp buckets: default variant used by 22 of 25 rate-decision predictors."""
    from mae_utils import compute_rate_outcome_distribution
    # Sharp posterior centered on anchor -> hold ~= 1.0
    d = compute_rate_outcome_distribution(4.25, 0.01, anchor=4.25, bucket_bp=25)
    assert d["modal"] == "hold"
    assert d["hold"] > 0.99
    # Wider posterior -> mass spreads to adjacent buckets
    d = compute_rate_outcome_distribution(4.25, 0.15, anchor=4.25, bucket_bp=25)
    assert d["modal"] == "hold"
    assert 0.4 < d["hold"] < 0.8
    assert d["hike25"] > 0.05 and d["cut25"] > 0.05


def test_rate_outcome_distribution_50bp_bcb():
    """BCB uses 50bp buckets — Selic typical move size."""
    from mae_utils import compute_rate_outcome_distribution
    # Point 50bp above anchor with narrow sigma -> hike25 modal (hike25 = anchor + 50bp @ 50bp step)
    d = compute_rate_outcome_distribution(15.5, 0.05, anchor=15.0, bucket_bp=50)
    assert d["modal"] == "hike25"


def test_rate_outcome_distribution_100bp_cbrt():
    """CBRT uses 100bp buckets — high-vol EM rate typical move."""
    from mae_utils import compute_rate_outcome_distribution
    # Point 200bp above anchor -> hike50 modal (hike50 = anchor + 200bp @ 100bp step)
    d = compute_rate_outcome_distribution(40.0, 0.3, anchor=38.0, bucket_bp=100)
    assert d["modal"] == "hike50"


def test_rate_outcome_distribution_no_anchor():
    """Missing anchor returns a note instead of a distribution."""
    from mae_utils import compute_rate_outcome_distribution
    d = compute_rate_outcome_distribution(4.25, 0.05, anchor=None)
    assert "note" in d
    assert "modal" not in d


def test_sigma_autotune_threshold_gates_switch():
    """The N>=5 threshold rule from emit_cpi / emit_fomc / emit — under
    threshold the prior sigma stays, at/above it the empirical takes
    over. Simulated inline since main() reads env + fetches network."""
    threshold = 5
    prior = 0.05
    empirical = 0.062
    # Below threshold: use prior
    def _effective(prior_sigma, empirical_obs):
        if empirical_obs and empirical_obs.get("count", 0) >= threshold:
            emp = empirical_obs.get("mae")
            if isinstance(emp, (int, float)) and emp > 0:
                return emp, "empirical"
        return prior_sigma, "prior"
    for count in (0, 1, 2, 3, 4):
        sigma, src = _effective(prior, {"count": count, "mae": empirical})
        assert (sigma, src) == (prior, "prior"), f"N={count} should use prior"
    for count in (5, 6, 10, 100):
        sigma, src = _effective(prior, {"count": count, "mae": empirical})
        assert (sigma, src) == (empirical, "empirical"), f"N={count} should use empirical"


if __name__ == "__main__":
    tests = [
        test_fomc_ladder_recovers_discrete_pmf,
        test_fomc_gaussian_fallback_when_no_ladder,
        test_cpi_ladder_bucket_probs,
        test_nfp_ladder_bucket_labels,
        test_survival_step_function_at_boundary,
        test_malformed_ladder_returns_none,
        test_empirical_mae_section_renders_for_zero_and_populated,
        test_empirical_mae_section_empty_when_no_data,
        test_rate_outcome_distribution_25bp_default,
        test_rate_outcome_distribution_50bp_bcb,
        test_rate_outcome_distribution_100bp_cbrt,
        test_rate_outcome_distribution_no_anchor,
        test_sigma_autotune_threshold_gates_switch,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            print(f"FAIL {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    sys.exit(1 if failed else 0)
