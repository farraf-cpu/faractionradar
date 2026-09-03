"""ISM Services PMI predictor + emitter. `v1-simple-blend`.

ISM Services (Non-Manufacturing) PMI is a diffusion index (0-100, 50 =
expansion threshold). Released ~3rd business day of each month, 2 days
after ISM Manufacturing. Also NOT on FRED (proprietary to ISM), so v1
uses consensus + naive last-known-value anchor. Mirror of emit_ism_mfg.py.

Services PMI is a bigger market mover than manufacturing on release day
because services are ~70% of US GDP.

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     ISM_SVC_RELEASE_DATE, ISM_SVC_DAYS_OUT, ISM_SVC_CONSENSUS,
     ISM_SVC_ANCHOR, MODEL_VERSION
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

# Same benchmark structure as ISM Mfg. Services consensus tends to be
# marginally looser (~1.1 pts) because services PMI is noisier m/m —
# hospitality/travel sub-index swings on holidays and weather.
MAE = {
    "consensus": 1.1,
    "anchor":    2.7,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-ism-svc] missing env: {key}", file=sys.stderr)
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
    if abs(delta) < 0.3:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    if value >= 55: return "solid expansion"
    if value >= 50: return "modest expansion"
    if value >= 45: return "modest contraction"
    return "sharp contraction"


def format_value(v: float) -> str:
    return f"{v:.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    return f"""# ISM Services PMI prediction — target {release} (T-{days_out})

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

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive last-known
anchor. ISM Services PMI is not published on FRED (proprietary) so no trend
sub-model in v1. Same architecture as ISM Manufacturing predictor.

Services is ~70% of US GDP so market reaction to ISM Services surprises is
typically larger than ISM Mfg. Sub-index breakout is what traders watch:
Business Activity, New Orders, Employment. Headline PMI is a composite.

Phase 2 target: add S&P Global Services PMI (released 3-5 days ahead) as
a leading sub-model. S&P Global publishes preliminary "flash" and final
readings; final correlates ~0.75 with ISM Services headline.
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
            print(f"[emit-ism-svc] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-ism-svc] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "ISM_SVC_RELEASE_DATE", "ISM_SVC_DAYS_OUT"):
        require_env(k)

    release = os.environ["ISM_SVC_RELEASE_DATE"]
    days_out = int(os.environ["ISM_SVC_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("ISM_SVC_CONSENSUS")
    anchor = parse_float("ISM_SVC_ANCHOR")

    if consensus is None and anchor is None:
        print("[emit-ism-svc] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-ism-svc] ISM Svc {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.2f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:.1f}")
    if anchor    is not None: print(f"  anchor:     {anchor:.1f}")

    prediction = {
        "eventSlug": f"ismsvc-{release}",
        "eventTitle": "US ISM Services PMI",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/ism-svc-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"ism-svc-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-ism-svc] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-ism-svc] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
