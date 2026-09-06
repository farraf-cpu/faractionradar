"""Fleet consistency: naming + model-card coverage across all predictors.

Verifies:
1. Every emit_*.py (plus emit.py for NFP) has a matching docs/<slug>-model-card.md
   Naming: emitter file uses underscores (emit_ism_mfg.py) but model cards
   use dashes (ism-mfg-model-card.md), so we normalize both directions.
2. Every emitter has a corresponding .github/workflows/predict-<slug>.yml
   (except emit.py which uses predict-nfp.yml).
3. Every emitter has a scripts/should_run_<slug>.py gate script
   (except emit.py which uses scripts/should_run.py).

Catches: new emitter added without a model card, workflow, or gate;
model card renamed without the emitter updating modelCardUrl; etc.

Run: python tests/test_fleet_consistency.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def emitter_slug(emit_file: Path) -> str:
    """emit_ism_mfg.py -> 'ism_mfg'; emit.py (NFP) -> 'nfp'."""
    name = emit_file.stem
    if name == "emit":
        return "nfp"
    assert name.startswith("emit_"), f"unexpected emitter filename: {name}"
    return name[len("emit_"):]


def dash_slug(underscore_slug: str) -> str:
    return underscore_slug.replace("_", "-")


def main() -> int:
    emitters = sorted(ROOT.glob("emit*.py"))
    emitters = [p for p in emitters if p.name in ("emit.py",) or p.name.startswith("emit_")]
    print(f"checking {len(emitters)} emitters for fleet consistency...")
    failed: list[str] = []

    for e in emitters:
        slug_u = emitter_slug(e)
        slug_d = dash_slug(slug_u)

        # 1. Model card exists (try dashed then underscored)
        card_dash = ROOT / "docs" / f"{slug_d}-model-card.md"
        card_us = ROOT / "docs" / f"{slug_u}-model-card.md"
        if not card_dash.exists() and not card_us.exists():
            failed.append(f"{e.name}: no model card ({card_dash.name} or {card_us.name})")

        # 2. Workflow exists
        wf_dash = ROOT / ".github" / "workflows" / f"predict-{slug_d}.yml"
        wf_us = ROOT / ".github" / "workflows" / f"predict-{slug_u}.yml"
        if not wf_dash.exists() and not wf_us.exists():
            failed.append(f"{e.name}: no workflow ({wf_dash.name} or {wf_us.name})")

        # 3. Gate script exists (NFP gate is scripts/should_run.py without slug)
        if slug_u == "nfp":
            gate = ROOT / "scripts" / "should_run.py"
        else:
            gate = ROOT / "scripts" / f"should_run_{slug_u}.py"
        if not gate.exists():
            failed.append(f"{e.name}: no gate script ({gate.name})")

    # 4. Every workflow uses .python-version instead of hardcoded version.
    # (Consistency guard added after fetch-kalshi.yml drifted to '3.13'.)
    wf_dir = ROOT / ".github" / "workflows"
    for wf in sorted(wf_dir.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        # Skip files that don't set up Python at all
        if "actions/setup-python" not in text:
            continue
        if "python-version-file" not in text:
            failed.append(f"{wf.name}: sets up python without .python-version file")

    # 5. All 4 test suites present (they're wired into ci/test.yml). If any
    # is deleted or renamed without updating test.yml, ci is silently narrower.
    required_tests = {
        "test_ladder_distribution.py",
        "test_all_emitters_have_mae.py",
        "test_all_emitters_render.py",
        "test_fleet_consistency.py",
    }
    have = {p.name for p in (ROOT / "tests").glob("test_*.py")}
    missing = required_tests - have
    if missing:
        failed.append(f"tests/ missing required suites: {sorted(missing)}")
    ci = (ROOT / ".github" / "workflows" / "test.yml").read_text(encoding="utf-8")
    for t in sorted(required_tests):
        if t not in ci:
            failed.append(f"ci/test.yml doesn't reference {t}")

    if failed:
        for f in failed:
            print(f"FAIL {f}")
        print(f"{len(failed)} failures / {len(emitters)} emitters + workflows checked")
        return 1
    print(f"{len(emitters)}/{len(emitters)} pass — fleet naming + python-version consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
