"""NZ GDP predictor. v1-simple-blend.

Bank of Korea publishes quarterly GDP q/q ~11 weeks
after quarter end at 10:45 KRWT (23:00 UTC prior day). Consensus-only:
FRED CHNGDPNQDSMEI doesn't exist; BOK Infoshare API integration
deferred to v1.1.

Value format: q/q %-change (e.g. "+0.4%").
Sub-models:
  - FF consensus (~0.15pp MAE - primary signal)

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     KRGDP_RELEASE_DATE, KRGDP_DAYS_OUT, KRGDP_CONSENSUS, MODEL_VERSION
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
    "consensus": 0.15,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-krgdp] missing env: {key}", file=sys.stderr)
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


def blend(consensus: float | None) -> tuple[float, float, list[str]]:
    parts = []
    if consensus is not None:
        parts.append(("consensus", consensus, MAE["consensus"]))
    if not parts:
        raise RuntimeError("blend called with no consensus")
    weights = [1.0 / m for (_, _, m) in parts]
    wsum = sum(weights)
    point = sum(w * v for (_, v, _), w in zip(parts, weights)) / wsum
    var = sum((w * m) ** 2 for (_, _, m), w in zip(parts, weights)) / (wsum ** 2)
    return point, math.sqrt(var), [p[0] for p in parts]


def lean_vs_consensus(point: float, consensus: float | None) -> str:
    if consensus is None:
        return "no consensus"
    delta = point - consensus
    if abs(delta) < 0.1:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.2f}pp"
    return f"below consensus by {abs(delta):.2f}pp"


def regime_annotation(value: float) -> str:
    if value >= 0.5:  return "solid monthly expansion"
    if value >= 0.1:  return "modest growth"
    if value >= -0.1: return "flat / stall"
    if value >= -0.3: return "contraction"
    return "sharp contraction"


def format_value(v: float) -> str:
    return f"{v:+.1f}%"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    used: list[str], lean: str) -> str:
    parts_tbl = f"| consensus | {'-' if consensus is None else f'{consensus:+.2f}%'} | {MAE['consensus']:.2f}pp |"
    return f"""# NZ GDP prediction - target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** q/q NZ GDP

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:+.2f}%, {point + sigma:+.2f}%]
- 95% CI: [{point - 2*sigma:+.2f}%, {point + 2*sigma:+.2f}%]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: consensus-only (BOK monthly GDP is not on FRED
cleanly; BOK API integration deferred to v1.1). Soft-skips when FF
consensus missing.

## Positioning

Third Phase 12 (KRW expansion) predictor. NZ GDP released by
BOK ~16 days after quarter end (early BOK release) at 10:45 KRWT (23:00 UTC prior day). Sits alongside
BoE Bank Rate + CA CPI in Phase 12 KRW trio.

## Caveats

NZ GDP is BOTH a real trader event (published monthly, unlike
Eurozone quarterly) AND a data source not covered on FRED. Consensus
is the only reliable signal for v1. Phase 12.1 target: integrate BOK
`kosis.kr` timeseries endpoint for a real trend anchor.

## Change log

- **v1-simple-blend ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})** - first ship. Third Phase 12 KRW predictor. Consensus-only pending BOK API integration.
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
            print(f"[emit-krgdp] worker -> {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-krgdp] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "KRGDP_RELEASE_DATE", "KRGDP_DAYS_OUT"):
        require_env(k)

    release = os.environ["KRGDP_RELEASE_DATE"]
    days_out = int(os.environ["KRGDP_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("KRGDP_CONSENSUS")

    if consensus is None:
        print("[emit-krgdp] consensus missing; nothing to blend - exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-krgdp] KRGDP {release} T-{days_out}: {format_value(point)} q/q "
          f"(sigma {sigma:.2f}pp, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus: {consensus:+.2f}%")

    prediction = {
        "eventSlug": f"krgdp-{release}",
        "eventTitle": "NZ GDP q/q",
        "country": "KRW",
        "releaseDate": release,
        "daysOut": days_out,
        "ourCall": {
            "value": format_value(point),
            "lean": lean,
            "ci68": [round(point - sigma, 2), round(point + sigma, 2)],
            "ci95": [round(point - 2 * sigma, 2), round(point + 2 * sigma, 2)],
            "publishedAt": datetime.now(timezone.utc).isoformat(),
            "model_version": model_version,
        },
        "grandMedian": None,
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/krgdp-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"krgdp-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-krgdp] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-krgdp] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
