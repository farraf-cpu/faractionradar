"""Entry point for the backtest harness. Dispatches to per-event backtest
modules and writes markdown results to backtest/results/.

Usage:
    python backtest/run_backtests.py --event retail --n 24
    python backtest/run_backtests.py --all --n 24
    python backtest/run_backtests.py --list

Env: FRED_API_KEY must be set for FRED fetches.

Available events (v1 rollout):
    retail — Retail Sales (v1 trend vs v1.1 trend + auto_leading)

Future: umich, housing, confidence, durable, existing, newhome, coreppi
(one per event upgraded 2026-09-07).
"""
from __future__ import annotations

import argparse
import importlib
import sys
from datetime import datetime
from pathlib import Path


# Registry: event_name -> (module_name, human_label)
# Extend as more per-event backtests land.
EVENTS = {
    "retail": ("backtest_retail", "US Advance Retail Sales m/m"),
    # TODO(next passes):
    # "umich": ("backtest_umich", "US UMich Consumer Sentiment Preliminary"),
    # "housing": ("backtest_housing", "US Housing Starts"),
    # "confidence": ("backtest_confidence", "US CB Consumer Confidence"),
    # "durable": ("backtest_durable", "US Durable Goods Orders m/m"),
    # "existing": ("backtest_existing", "US Existing Home Sales"),
    # "newhome": ("backtest_newhome", "US New Home Sales"),
    # "coreppi": ("backtest_coreppi", "US Core PPI m/m"),
}


def run_one(event: str, n: int) -> tuple[bool, str, Path | None]:
    """Run a single event backtest. Returns (ok, message, output_path)."""
    if event not in EVENTS:
        return False, f"unknown event: {event}", None
    module_name, _label = EVENTS[event]
    try:
        mod = importlib.import_module(module_name)
    except ImportError as e:
        return False, f"import failed for {module_name}: {e}", None
    report = mod.run(n=n)
    out_dir = Path(__file__).parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{event}-{datetime.now().strftime('%Y-%m-%d')}.md"
    out_path.write_text(report, encoding="utf-8")
    return True, f"wrote {out_path.relative_to(Path(__file__).parent.parent)}", out_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=str,
                        help="Event slug (see --list for options)")
    parser.add_argument("--all", action="store_true",
                        help="Run backtests for all registered events")
    parser.add_argument("--list", action="store_true",
                        help="List available event backtests + exit")
    parser.add_argument("--n", type=int, default=24,
                        help="Rolling window size (default: 24 recent releases)")
    args = parser.parse_args()

    if args.list:
        print("Available event backtests:")
        for k, (_m, label) in sorted(EVENTS.items()):
            print(f"  {k:12} — {label}")
        return 0

    if not args.event and not args.all:
        parser.print_help(sys.stderr)
        return 2

    targets = list(EVENTS.keys()) if args.all else [args.event]
    fail = 0
    for evt in targets:
        ok, msg, _ = run_one(evt, args.n)
        prefix = "  ok" if ok else "FAIL"
        print(f"{prefix} · {evt:12} · {msg}")
        if not ok:
            fail += 1
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
