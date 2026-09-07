"""Shared backtest harness — FRED history replay + MAE aggregation.

Backtest v1 scope: FRED-based sub-models only. See backtest/README.md
for the honest caveats (revision drift, consensus/market omission).

Public API:
    fetch_fred_history(api_key, series_id, start_date, end_date) -> list[dict]
    slice_at_date(obs, cutoff_date) -> list[dict]  (point-in-time filter)
    replay(predictor_fn, events, series_needed, api_key) -> BacktestResult
    aggregate(errors: list[float]) -> dict  (MAE, RMSE, bias, N)
    format_report(event_name, per_release_rows, summary_v1, summary_v1_1) -> str
"""
from __future__ import annotations

import json
import math
import statistics
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"


@dataclass
class BacktestRow:
    """One historical event's replay result."""
    release_date: str      # YYYY-MM-DD
    v1_pred: float | None
    v1_1_pred: float | None
    actual: float | None
    v1_err: float | None = None
    v1_1_err: float | None = None

    def __post_init__(self):
        if self.v1_pred is not None and self.actual is not None:
            self.v1_err = self.v1_pred - self.actual
        if self.v1_1_pred is not None and self.actual is not None:
            self.v1_1_err = self.v1_1_pred - self.actual


@dataclass
class BacktestSummary:
    """Aggregate statistics for a v1 or v1.1 replay."""
    label: str
    n: int
    mae: float | None
    rmse: float | None
    bias: float | None
    n_valid: int  # count of rows where prediction was non-null

    @classmethod
    def from_errors(cls, label: str, errors: list[float | None]) -> "BacktestSummary":
        valid = [e for e in errors if e is not None]
        if not valid:
            return cls(label=label, n=len(errors), mae=None, rmse=None,
                       bias=None, n_valid=0)
        mae = sum(abs(e) for e in valid) / len(valid)
        rmse = math.sqrt(sum(e * e for e in valid) / len(valid))
        bias = sum(valid) / len(valid)
        return cls(label=label, n=len(errors), mae=mae, rmse=rmse,
                   bias=bias, n_valid=len(valid))


def fetch_fred_history(api_key: str, series_id: str,
                       limit: int = 200) -> list[dict] | None:
    """Fetch full historical observations for a FRED series (newest first).
    Returns list of {date: YYYY-MM-DD, value: float-str} or None on failure.

    Unlike the live predictor helpers which fetch limit=3-8, backtests need
    the full monthly history — bumps default limit to 200 (17 years of
    monthly data, plenty for a 24-release rolling window).
    """
    url = ("https://api.stlouisfed.org/fred/series/observations?"
           f"series_id={urllib.parse.quote(series_id)}"
           f"&api_key={urllib.parse.quote(api_key)}"
           "&file_type=json"
           "&sort_order=desc"
           f"&limit={limit}")
    req = urllib.request.Request(url, headers={"user-agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            data = json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"[backtest] FRED fetch failed for {series_id}: {e}")
        return None
    obs = data.get("observations") or []
    return [o for o in obs if o.get("value") and o["value"] != "."]


def slice_at_date(obs: list[dict], cutoff_date: str) -> list[dict]:
    """Point-in-time filter: return obs dated < cutoff_date.
    Strict less-than to avoid using the observation being backtested
    as its own prediction input.

    cutoff_date format: YYYY-MM-DD
    Assumes obs are sorted newest first (FRED sort_order=desc convention).
    """
    return [o for o in obs if o.get("date", "") < cutoff_date]


def mom_pct_from_levels(levels: list[float]) -> list[float]:
    """Compute m/m %-changes from a levels list.
    levels[0] is newest; result[0] is the newest m/m %.
    """
    out = []
    for i in range(len(levels) - 1):
        prev = levels[i + 1]
        curr = levels[i]
        if prev and prev > 0:
            out.append((curr - prev) / prev * 100.0)
    return out


def obs_to_floats(obs: list[dict]) -> list[float]:
    """Extract numeric values from FRED obs list, in order (newest first)."""
    out = []
    for o in obs:
        v = o.get("value")
        if v and v != ".":
            try:
                out.append(float(v))
            except ValueError:
                pass
    return out


def format_report(event_name: str,
                  rows: list[BacktestRow],
                  summaries: list[BacktestSummary],
                  caveats: str = "") -> str:
    """Render a markdown backtest report."""
    header = (
        f"# Backtest — {event_name}\n\n"
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}\n"
        f"**Releases replayed:** {len(rows)}\n\n"
    )
    tbl_header = (
        "## Per-release replay\n\n"
        "| release_date | v1_pred | v1.1_pred | actual | v1_err | v1.1_err |\n"
        "|--------------|---------|-----------|--------|--------|----------|\n"
    )

    def fmt(v: float | None) -> str:
        return "—" if v is None else f"{v:+.3f}"

    body_rows = "\n".join(
        f"| {r.release_date} | {fmt(r.v1_pred)} | {fmt(r.v1_1_pred)} | "
        f"{fmt(r.actual)} | {fmt(r.v1_err)} | {fmt(r.v1_1_err)} |"
        for r in rows
    )

    summary_section = "\n\n## Aggregate\n\n"
    summary_section += "| model | N (valid) | MAE | RMSE | bias |\n"
    summary_section += "|-------|-----------|-----|------|------|\n"
    for s in summaries:
        summary_section += (
            f"| {s.label} | {s.n_valid} / {s.n} | "
            f"{fmt(s.mae)} | {fmt(s.rmse)} | {fmt(s.bias)} |\n"
        )

    # Improvement summary if we have both v1 and v1.1
    v1s = [s for s in summaries if s.label == "v1"]
    v11s = [s for s in summaries if s.label == "v1.1"]
    improvement = ""
    if v1s and v11s and v1s[0].mae and v11s[0].mae:
        delta = v1s[0].mae - v11s[0].mae
        pct = (delta / v1s[0].mae) * 100.0
        direction = "reduction" if delta > 0 else "REGRESSION"
        improvement = (
            f"\n**v1 → v1.1 MAE {direction}:** "
            f"{delta:+.3f} ({pct:+.1f}%)\n"
        )

    caveats_section = f"\n## Caveats\n\n{caveats}\n" if caveats else ""

    return (header + tbl_header + body_rows + summary_section +
            improvement + caveats_section)


def walk_recent_releases(release_dates: list[str], n: int = 24) -> list[str]:
    """Trim a full history of release dates down to the N most recent
    with reasonable spacing. Assumes input is sorted ascending."""
    if not release_dates:
        return []
    return release_dates[-n:] if len(release_dates) >= n else release_dates


DEFAULT_CAVEATS = """- **Revision drift:** current FRED values may differ from first-print.
  Backtest MAE is optimistic vs live trading. Fix requires ALFRED.
- **Consensus omitted:** v1 baseline is "trend only" — no consensus
  input, since FF forecast history isn't archived. Live v1 blends
  consensus + trend; live v1.1 blends consensus + trend + new sub-model.
- **Coefficient defaults:** measures the pre-empirical coefficients
  shipped 2026-09-07. Refit is a separate follow-up pass.
"""
