"""Coefficient sweep + refit analyzer.

Reads the markdown artifacts produced by backtest/run_backtests.py and
computes MAE-minimizing coefficient values per predictor using OLS on
the residuals. Then reports:

- shipped coefficient
- OLS-optimal coefficient
- MAE at shipped
- MAE at optimal (simulated)
- whether v1.1 with optimal beats v1

Refit rules (matches each backtest_<event>.py formulation):

Additive shocks (feature adds a scaled adjustment to v1):
  v1.1 = v1 + beta * feature
  retail:  feature = TOTALSA m/m %-change, beta_shipped =  0.22
  umich:   feature = WTI m/m %-change,      beta_shipped = -0.4

Multiplicative shocks (feature scales a factor by v1):
  v1.1 = v1 * (1 + beta * feature)
  existing:   feature = MORTGAGE30US 2mo rate change bp, beta_shipped = -0.005
  newhome:    feature = MORTGAGE30US 4wk rate change bp, beta_shipped = -0.007
  confidence: feature = UMCSENT 2mo momentum,             beta_shipped =  0.75

Independent-point sub-models (aux series used as its own point estimate,
NOT blended with v1 in backtest — refit finds an optimal blend weight):
  v1.1 = aux_trend  (as shipped; wrong architecture for backtest)
  refit: v1.1 = w * v1_trend + (1-w) * aux_trend  (find optimal w)
  housing: aux = PERMIT 3-mo trend
  coreppi: aux = PPICMM 6-mo m/m mean

Usage:
  python backtest/analyze_sweeps.py [results_dir]

  Defaults to ./backtest/results if run from repo root, else takes an
  explicit dir path (e.g. downloaded workflow artifact).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


# Per-event refit parameters.
#
# formula:
#   "additive"        v1.1 = v1_pred + beta * feature
#                     feature reconstructable from (v1.1 - v1) / beta_shipped
#   "multiplicative"  v1.1 = v1_pred * (1 + beta * feature)
#                     feature reconstructable from ((v1.1/v1) - 1) / beta_shipped
#   "blend"           v1.1 = aux_trend (backtest measured aux alone).
#                     Refit blend weight w in [0, 1]:
#                     v1.1_refit = w * v1_pred + (1-w) * aux_trend
#                     Since backtest v1.1_pred == aux_trend, we get aux = v1.1
EVENTS = {
    "retail":     {"formula": "additive",       "beta_shipped":  0.22,   "name": "AUTO_SHARE_COEFF"},
    "umich":      {"formula": "additive",       "beta_shipped": -0.4,    "name": "OIL_SHOCK_COEFF"},
    "existing":   {"formula": "multiplicative", "beta_shipped": -0.005,  "name": "MORTGAGE_SENSITIVITY"},
    "newhome":    {"formula": "multiplicative", "beta_shipped": -0.007,  "name": "MORTGAGE_SENSITIVITY"},
    "confidence": {"formula": "multiplicative", "beta_shipped":  0.75,   "name": "UMICH_CB_CORRELATION"},
    "housing":    {"formula": "blend",          "beta_shipped":  None,   "name": "blend_weight_v1"},
    "coreppi":    {"formula": "blend",          "beta_shipped":  None,   "name": "blend_weight_v1"},
}


ROW_RE = re.compile(
    r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|"
    r"\s*([+-]?\d*\.?\d+|—)\s*\|"
    r"\s*([+-]?\d*\.?\d+|—)\s*\|"
    r"\s*([+-]?\d*\.?\d+|—)\s*\|"
)


def parse_report(md_text: str) -> list[tuple[str, float, float, float]]:
    """Return list of (release_date, v1_pred, v1_1_pred, actual) tuples.
    Skips rows with any missing (—) fields."""
    out = []
    for line in md_text.splitlines():
        m = ROW_RE.match(line)
        if not m:
            continue
        rd, v1s, v11s, actuals = m.group(1), m.group(2), m.group(3), m.group(4)
        if "—" in (v1s, v11s, actuals):
            continue
        try:
            out.append((rd, float(v1s), float(v11s), float(actuals)))
        except ValueError:
            continue
    return out


@dataclass
class RefitResult:
    event: str
    coef_name: str
    n: int
    shipped_beta: float | None
    optimal_beta: float | None
    mae_v1: float
    mae_v1_1_shipped: float
    mae_v1_1_optimal: float
    beats_v1: bool
    formula: str


def refit_additive(rows: list[tuple[str, float, float, float]],
                   beta_shipped: float) -> tuple[float, float]:
    """OLS: minimize sum(v1 + beta * f - actual)² -> beta = sum(f * (actual - v1)) / sum(f²).
    Returns (optimal_beta, mae_at_optimal)."""
    features = []
    residuals = []
    for _rd, v1, v11, actual in rows:
        f = (v11 - v1) / beta_shipped
        r = actual - v1
        features.append(f)
        residuals.append(r)
    num = sum(f * r for f, r in zip(features, residuals))
    den = sum(f * f for f in features)
    beta_opt = num / den if den > 1e-12 else 0.0
    errors = [(v1 + beta_opt * f - actual)
              for (_rd, v1, _v11, actual), f in zip(rows, features)]
    mae = sum(abs(e) for e in errors) / len(errors) if errors else float("nan")
    return beta_opt, mae


def refit_multiplicative(rows: list[tuple[str, float, float, float]],
                         beta_shipped: float) -> tuple[float, float]:
    """v1.1 = v1 * (1 + beta * f). Define g = v1 * f, then v1.1 = v1 + beta * g.
    Same OLS as additive with feature = g."""
    features_g = []
    residuals = []
    for _rd, v1, v11, actual in rows:
        # Reconstruct f from (v11/v1 - 1) / beta_shipped
        f = ((v11 / v1) - 1.0) / beta_shipped if abs(v1) > 1e-12 else 0.0
        g = v1 * f
        r = actual - v1
        features_g.append(g)
        residuals.append(r)
    num = sum(g * r for g, r in zip(features_g, residuals))
    den = sum(g * g for g in features_g)
    beta_opt = num / den if den > 1e-12 else 0.0
    errors = [(v1 + beta_opt * g - actual)
              for (_rd, v1, _v11, actual), g in zip(rows, features_g)]
    mae = sum(abs(e) for e in errors) / len(errors) if errors else float("nan")
    return beta_opt, mae


def refit_blend(rows: list[tuple[str, float, float, float]]) -> tuple[float, float]:
    """v1.1_pred (shipped) = aux_trend. Refit as:
    v1.1_refit = w * v1_trend + (1-w) * aux_trend

    Minimize MSE:
    sum((w*v1 + (1-w)*aux - actual)²)
    d/dw: 2 sum((v1 - aux) * (w*v1 + (1-w)*aux - actual)) = 0
    w = sum((v1 - aux) * (actual - aux)) / sum((v1 - aux)²)
    """
    num = 0.0
    den = 0.0
    for _rd, v1, aux, actual in rows:
        diff = v1 - aux
        num += diff * (actual - aux)
        den += diff * diff
    w_opt = num / den if den > 1e-12 else 1.0
    # Clamp to [0, 1] for interpretability; report the unclamped in the
    # printout so a >1 or <0 result is visible as a sign that aux is
    # actively harmful or unnecessary.
    w_clamped = max(0.0, min(1.0, w_opt))
    errors = [(w_clamped * v1 + (1 - w_clamped) * aux - actual)
              for (_rd, v1, aux, actual) in rows]
    mae = sum(abs(e) for e in errors) / len(errors) if errors else float("nan")
    return w_opt, mae


def analyze(results_dir: Path) -> list[RefitResult]:
    out: list[RefitResult] = []
    for event, cfg in EVENTS.items():
        # Find the report file
        candidates = list(results_dir.glob(f"{event}-*.md"))
        if not candidates:
            print(f"[warn] no {event}-*.md report found in {results_dir}")
            continue
        report = candidates[0]
        rows = parse_report(report.read_text(encoding="utf-8"))
        if not rows:
            print(f"[warn] {event}: no parseable rows")
            continue
        # MAE v1 = mean |v1 - actual|
        mae_v1 = sum(abs(v1 - actual) for _rd, v1, _v11, actual in rows) / len(rows)
        # MAE v1.1 (shipped) = mean |v1.1 - actual|
        mae_v11_shipped = sum(
            abs(v11 - actual) for _rd, _v1, v11, actual in rows
        ) / len(rows)
        formula = cfg["formula"]
        beta_shipped = cfg["beta_shipped"]

        if formula == "additive":
            beta_opt, mae_opt = refit_additive(rows, beta_shipped)
        elif formula == "multiplicative":
            beta_opt, mae_opt = refit_multiplicative(rows, beta_shipped)
        elif formula == "blend":
            beta_opt, mae_opt = refit_blend(rows)
        else:
            raise ValueError(f"unknown formula: {formula}")

        out.append(RefitResult(
            event=event,
            coef_name=cfg["name"],
            n=len(rows),
            shipped_beta=beta_shipped,
            optimal_beta=beta_opt,
            mae_v1=mae_v1,
            mae_v1_1_shipped=mae_v11_shipped,
            mae_v1_1_optimal=mae_opt,
            beats_v1=(mae_opt < mae_v1),
            formula=formula,
        ))
    return out


def format_report(results: list[RefitResult]) -> str:
    lines = ["# Coefficient sweep + refit\n"]
    lines.append("| event | n | coefficient | shipped | optimal | MAE v1 | MAE v1.1 shipped | MAE v1.1 optimal | beats v1? |")
    lines.append("|-------|---|-------------|---------|---------|--------|-------------------|-------------------|-----------|")
    for r in results:
        shipped_s = f"{r.shipped_beta:+.4f}" if r.shipped_beta is not None else "—"
        optimal_s = f"{r.optimal_beta:+.4f}" if r.optimal_beta is not None else "—"
        beats = "YES" if r.beats_v1 else "no"
        lines.append(
            f"| {r.event} | {r.n} | `{r.coef_name}` | {shipped_s} | {optimal_s} | "
            f"{r.mae_v1:.4f} | {r.mae_v1_1_shipped:.4f} | {r.mae_v1_1_optimal:.4f} | {beats} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("- **additive** (`retail`, `umich`): OLS on residuals against reconstructed feature. Optimal beta from sum(f*r)/sum(f²).")
    lines.append("- **multiplicative** (`existing`, `newhome`, `confidence`): same OLS with feature g = v1*f.")
    lines.append("- **blend** (`housing`, `coreppi`): backtest v1.1 was aux alone. Refit is w*v1 + (1-w)*aux. Optimal w minimizes MSE.")
    lines.append("  - w > 1 or w = 1: v1 alone is better than blending in aux -> **aux sub-model should be dropped, not refit**.")
    lines.append("  - 0 < w < 1: blend improves; ship v1.1 with inverse-MAE blend and refit MAE weights on aux.")
    return "\n".join(lines)


def main() -> int:
    if len(sys.argv) > 1:
        results_dir = Path(sys.argv[1])
    else:
        results_dir = Path(__file__).parent / "results"
    if not results_dir.exists():
        print(f"[error] results dir not found: {results_dir}", file=sys.stderr)
        return 1
    results = analyze(results_dir)
    if not results:
        print("[error] no results parseable", file=sys.stderr)
        return 1
    report = format_report(results)
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
