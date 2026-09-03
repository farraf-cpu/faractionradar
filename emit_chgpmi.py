"""Chicago PMI predictor + emitter. `v1-simple-blend`.

Monthly release, last business day of month, 09:45 ET by ISM-Chicago /
MNI Indicators. Diffusion index (0-100, 50 = expansion threshold).
Regional (Midwest / Chicago) manufacturing gauge — leads national ISM Mfg
by ~2 business days.

Sub-models:
  - Bloomberg / FF consensus (~2.5 index points MAE)
  - Last-known anchor (~4.0 pts MAE — naive persistence)

Not on FRED (MNI Indicators subscription only), so no trend sub-model.
Same architecture as ISM Mfg/Svc predictors.

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     CHGPMI_RELEASE_DATE, CHGPMI_DAYS_OUT, CHGPMI_CONSENSUS,
     CHGPMI_ANCHOR, MODEL_VERSION
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

MAE = {
    "consensus": 2.5,
    "anchor":    4.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-chgpmi] missing env: {key}", file=sys.stderr)
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
    if abs(delta) < 0.5:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    if value >= 55: return "solid regional expansion"
    if value >= 50: return "modest regional expansion"
    if value >= 45: return "modest regional contraction"
    return "sharp regional contraction"


def format_value(v: float) -> str:
    return f"{v:.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    return f"""# Chicago PMI prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** Chicago Business Barometer (0-100 diffusion index)

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

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
MNI Chicago Business Barometer is subscription-only (not on FRED), so no
trend sub-model in v1. Same architecture as ISM Mfg/Svc predictors.

Chicago PMI leads ISM Manufacturing by ~2 business days (releases last
business day of month; ISM Mfg is 1st business day of following month).

## Phase 2 targets

- **National ISM Mfg cross-check** — historical Chicago→ISM correlation is
  ~0.75; use Chicago as a nowcast input to ISM Mfg predictor
- **New Orders sub-index** — Chicago publishes sub-indices; New Orders leads
  headline by 1-2 months

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 22nd event covered.
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
            print(f"[emit-chgpmi] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-chgpmi] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "CHGPMI_RELEASE_DATE", "CHGPMI_DAYS_OUT"):
        require_env(k)

    release = os.environ["CHGPMI_RELEASE_DATE"]
    days_out = int(os.environ["CHGPMI_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("CHGPMI_CONSENSUS")
    anchor = parse_float("CHGPMI_ANCHOR")

    if consensus is None and anchor is None:
        print("[emit-chgpmi] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-chgpmi] ChicagoPMI {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.1f}")
    if anchor    is not None: print(f"  anchor:     {anchor:.1f}")

    prediction = {
        "eventSlug": f"chgpmi-{release}",
        "eventTitle": "US Chicago PMI",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/chgpmi-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"chgpmi-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-chgpmi] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-chgpmi] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
