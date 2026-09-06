"""Sanity: every emit_*.py has empirical MAE + sigma auto-tune wired.

Runs on every predictor in the repo. Verifies:
1. Module imports without error
2. Module exports build_report_md
3. build_report_md accepts empirical_mae, sigma_source, prior_sigma kwargs
4. Module imports from mae_utils

Catches drift when a new emitter is added without the standard wiring
or when a refactor accidentally strips the mae_utils integration from
an existing file.

Run: python tests/test_all_emitters_have_mae.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def all_emitters() -> list[str]:
    """Every emit_*.py module name in the repo, minus emit.py (NFP orchestrator)."""
    names = []
    for p in sorted(ROOT.glob("emit_*.py")):
        names.append(p.stem)
    return names


def check_module(name: str) -> tuple[bool, str]:
    """Return (ok, reason). ok=True means the emitter has full wiring."""
    try:
        mod = __import__(name)
    except Exception as e:
        return False, f"import failed: {type(e).__name__}: {e}"

    if not hasattr(mod, "build_report_md"):
        return False, "missing build_report_md"

    sig_vars = mod.build_report_md.__code__.co_varnames
    required = {"empirical_mae", "sigma_source", "prior_sigma"}
    missing = required - set(sig_vars)
    if missing:
        return False, f"build_report_md missing kwargs: {sorted(missing)}"

    if not hasattr(mod, "fetch_empirical_mae"):
        return False, "missing fetch_empirical_mae"

    return True, "ok"


def main() -> int:
    names = all_emitters()
    print(f"checking {len(names)} emitters...")
    failed = []
    for name in names:
        ok, reason = check_module(name)
        if not ok:
            print(f"FAIL {name}: {reason}")
            failed.append(name)
    print(f"{len(names) - len(failed)}/{len(names)} pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
