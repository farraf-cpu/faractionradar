"""Smoke: every emit_*.py's build_report_md renders without exceptions.

Introspects each emitter's build_report_md signature and calls it with
sensible fake args, verifying the returned .md string is non-trivial.
Catches template regressions (bad f-string, missing variable, broken
format spec) across all 117 predictors on every push.

Run: python tests/test_all_emitters_render.py
"""
from __future__ import annotations

import glob
import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def build_fake_args(fn) -> list:
    """Infer sensible fake positional args from build_report_md signature."""
    args: list = []
    for pname, pparam in inspect.signature(fn).parameters.items():
        if pparam.default is not inspect.Parameter.empty:
            continue  # skip kwargs with defaults
        anno_str = str(pparam.annotation)
        # Order matters: list check must precede str-in-annotation fallback
        if "list" in anno_str or pname == "used":
            args.append(["consensus"])
        elif pname == "lean":
            args.append("in line")
        elif pname == "release":
            args.append("2026-01-01")
        elif pname == "model_version":
            args.append("v1-test")
        elif pname == "days_out":
            args.append(1)
        elif pparam.annotation in (float, int) or pname in (
            "point", "sigma", "consensus", "anchor", "trend"
        ):
            args.append(2.0)
        else:
            args.append(None)
    return args


def main() -> int:
    emitters = sorted(glob.glob(str(ROOT / "emit_*.py")))
    print(f"rendering {len(emitters)} emitters...")
    failed: list[str] = []
    for path in emitters:
        name = Path(path).stem
        try:
            mod = importlib.import_module(name)
            fn = mod.build_report_md
            args = build_fake_args(fn)
            md = fn(*args)
            if not isinstance(md, str) or len(md) < 100:
                failed.append(f"{name}: output too short or wrong type")
        except Exception as e:
            failed.append(f"{name}: {type(e).__name__}: {e}")
    if failed:
        for f in failed[:20]:
            print(f"FAIL {f}")
        if len(failed) > 20:
            print(f"...+{len(failed)-20} more")
        print(f"{len(failed)}/{len(emitters)} failures")
        return 1
    print(f"{len(emitters)}/{len(emitters)} render clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
