"""ISM Manufacturing PMI predictor + emitter. `v1-simple-blend`.

ISM Manufacturing PMI is a diffusion index (0-100 scale, 50 = expansion
threshold). Released 1st business day of each month at 10:00 ET by Institute
for Supply Management.

Unlike CPI/PCE/PPI, ISM PMI is NOT published on FRED — it's proprietary
to ISM. That constrains v1 to consensus-only with FRED regional Fed
manufacturing indices as a *directional* proxy (regional surveys lead ISM
by ~2 weeks). v1 ships consensus-only; regional proxy sub-model lands with
v1.1 once the exact FRED series IDs are verified against ISM correlation.

Value format: index level (e.g. "48.5", "50.2"), NOT a m/m %-change.

Sub-models:
  - Bloomberg / FF consensus (~1.0 index point MAE — analysts get most of
    the signal from ISM's own advance surveys and regional Fed peers)

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     ISM_MFG_RELEASE_DATE, ISM_MFG_DAYS_OUT, ISM_MFG_CONSENSUS, MODEL_VERSION
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0"

# Historical MAE benchmarks (index points on the 0-100 ISM PMI scale).
# Consensus MAE ~1.0 is the industry benchmark for headline ISM Manufacturing
# — analysts triangulate from ISM's own preliminary survey + regional Fed
# peers, so aggregate consensus is quite tight. Anchor MAE ~2.5 reflects
# naive-persistence (assume prev-month prints again).
MAE = {
    "consensus": 1.0,
    "anchor":    2.5,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-ism-mfg] missing env: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def parse_float(env_key: str) -> float | None:
    v = os.environ.get(env_key)
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def blend(consensus: float | None,
          anchor: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if anchor is not None:
        parts.append(("anchor", anchor, MAE["anchor"]))
    if not parts:
        raise RuntimeError("blend called with all sub-models missing")
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.3:  # ~0.3 index points = noise-level on ISM
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    """Diffusion-index regime label. 50 is expansion/contraction threshold."""
    if value >= 55: return "solid expansion"
    if value >= 50: return "modest expansion"
    if value >= 45: return "modest contraction"
    return "sharp contraction"


def format_value(v: float) -> str:
    """ISM convention: one decimal, no unit sign."""
    return f"{v:.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    return f"""# ISM Manufacturing PMI prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** (diffusion index; 50 = expansion threshold)

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:.1f}, {point + sigma:.1f}]
- 95% CI: [{point - 2*sigma:.1f}, {point + 2*sigma:.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + optional
last-known-value anchor. ISM PMI is NOT on FRED (proprietary to Institute
for Supply Management) so no persistence trend sub-model in v1.

Phase 2 target adds regional Fed nowcasts as a leading-indicator sub-model:
Empire State (NY Fed), Philly Fed, Dallas Fed, Kansas City Fed, Richmond
Fed. All publish current-activity diffusion indexes 5-10 days ahead of ISM.
FRB Cleveland shows the aggregate of these regional indices lag ISM by
0.85 correlation — a proper weighted-average sub-model would tighten our
MAE from ~1.0 to ~0.7 index points.
"""


def append_ledger(payload: dict) -> None:
    ledger = ROOT / "predictions.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": auth_key,
            "user-agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[emit-ism-mfg] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-ism-mfg] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "ISM_MFG_RELEASE_DATE", "ISM_MFG_DAYS_OUT"):
        require_env(k)

    release = os.environ["ISM_MFG_RELEASE_DATE"]
    days_out = int(os.environ["ISM_MFG_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("ISM_MFG_CONSENSUS")
    anchor = parse_float("ISM_MFG_ANCHOR")  # last-known value from FF's "previous" field, populated by workflow

    if consensus is None and anchor is None:
        print("[emit-ism-mfg] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-ism-mfg] ISM Mfg {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.2f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.1f}")
    if anchor    is not None: print(f"  anchor:     {anchor:.1f}")

    prediction = {
        "eventSlug": f"ismmfg-{release}",
        "eventTitle": "US ISM Manufacturing PMI",
        "country": "USD",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma, 1), round(point + sigma, 1)],
            "ci95": [round(point - 2 * sigma, 1), round(point + 2 * sigma, 1)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/ism-mfg-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"ismmfg-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-ism-mfg] wrote {report_path.relative_to(ROOT)}")

    ledger_row = {
        "publishedAt": prediction["ourCall"]["publishedAt"],
        "eventSlug": prediction["eventSlug"],
        "daysOut": days_out,
        "modelVersion": model_version,
        "ourCall": prediction["ourCall"]["value"],
        "ci68": prediction["ourCall"]["ci68"],
        "grandMedian": None,
        "reportPath": str(report_path.relative_to(ROOT)),
    }
    append_ledger(ledger_row)
    print(f"[emit-ism-mfg] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
