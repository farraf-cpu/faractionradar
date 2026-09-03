"""Dallas Fed Manufacturing (Texas Manufacturing Outlook Survey) predictor +
emitter. `v1-simple-blend`.

Monthly release, ~last Monday of month, 10:30 ET by Federal Reserve Bank
of Dallas. General Business Activity diffusion index where 0 = neutral
(same scale as Empire/Philly). Third regional Fed survey each month
(after Empire ~15th and Philly ~3rd Thursday).

Sub-models:
  - Bloomberg / FF consensus (~5 index points MAE)
  - Last-known anchor (~7 pts MAE)

No FRED trend in v1 — Dallas Fed's headline general-business series ID
needs verification before wiring. Add real trend in Phase 2 once verified.

Env: UPLOAD_AUTH_KEY, CALENDAR_WORKER_URL,
     DALLAS_RELEASE_DATE, DALLAS_DAYS_OUT, DALLAS_CONSENSUS,
     DALLAS_ANCHOR, MODEL_VERSION
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
    "consensus": 5.0,
    "anchor":    7.0,
}


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit-dallas] missing env: {key}", file=sys.stderr)
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
    if abs(delta) < 1.0:
        return "in line with consensus"
    if delta > 0:
        return f"above consensus by {delta:.1f} pts"
    return f"below consensus by {abs(delta):.1f} pts"


def regime_annotation(value: float) -> str:
    if value >= 10:  return "solid Texas expansion"
    if value >= 0:   return "modest Texas expansion"
    if value >= -10: return "modest Texas contraction"
    return "sharp Texas contraction"


def format_value(v: float) -> str:
    return f"{v:+.1f}"


def build_report_md(point: float, sigma: float, release: str, days_out: int,
                    model_version: str, consensus: float | None,
                    anchor: float | None, used: list[str], lean: str) -> str:
    parts_tbl = "\n".join(
        f"| {name} | {'—' if v is None else f'{v:+.1f}'} | {MAE[name]:.1f} pts |"
        for name, v in (("consensus", consensus), ("anchor", anchor))
    )
    return f"""# Dallas Fed Manufacturing prediction — target {release} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{format_value(point)}** Dallas Fed General Business Activity

- Regime: {regime_annotation(point)}
- 68% CI: [{point - sigma:+.1f}, {point + sigma:+.1f}]
- 95% CI: [{point - 2*sigma:+.1f}, {point + 2*sigma:+.1f}]
- Lean vs consensus: {lean}
- Sub-models used: {', '.join(used)}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
{parts_tbl}

## Method

`v1-simple-blend`: inverse-MAE-weighted mean of consensus + naive anchor.
FRED trend sub-model deferred to v1.1 pending series-ID verification.

## Positioning

Third regional Fed survey each month (after Empire ~15th, Philly ~3rd
Thursday). Texas leans oil-heavy — Dallas is the highest-beta regional
Fed survey to WTI crude swings. Solid input to the 5-Fed composite
proxy for ISM Mfg.

## Phase 2 targets

- **FRED trend sub-model** — verify Dallas Fed general-business series and wire in
- **Production sub-index** — cleaner read on physical output
- **WTI crude sensitivity overlay** — Dallas is oil-beta relative to other regional Feds

## Change log

- **v1-simple-blend (2026-09-03)** — first ship. 25th event covered.
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
            print(f"[emit-dallas] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit-dallas] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for k in ("UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "DALLAS_RELEASE_DATE", "DALLAS_DAYS_OUT"):
        require_env(k)

    release = os.environ["DALLAS_RELEASE_DATE"]
    days_out = int(os.environ["DALLAS_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-simple-blend")

    consensus = parse_float("DALLAS_CONSENSUS")
    anchor = parse_float("DALLAS_ANCHOR")

    if consensus is None and anchor is None:
        print("[emit-dallas] all sub-models missing; nothing to blend — exit 0 (soft skip)")
        return

    point, sigma, used = blend(consensus, anchor)
    lean = lean_vs_consensus(point, consensus)

    print(f"[emit-dallas] Dallas {release} T-{days_out}: {format_value(point)} "
          f"(sigma {sigma:.1f} pts, {regime_annotation(point)}, used: {', '.join(used)})")
    if consensus is not None: print(f"  consensus:  {consensus:+.1f}")
    if anchor    is not None: print(f"  anchor:     {anchor:+.1f}")

    prediction = {
        "eventSlug": f"dallas-{release}",
        "eventTitle": "US Dallas Fed Manufacturing Index",
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
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/dallas-model-card.md",
    }

    report_md = build_report_md(point, sigma, release, days_out, model_version,
                                consensus, anchor, used, lean)
    year_month = release[:7]
    report_path = ROOT / "reports" / year_month / f"dallas-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit-dallas] wrote {report_path.relative_to(ROOT)}")

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
    print(f"[emit-dallas] appended predictions.jsonl")

    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    post_to_worker(worker_url, os.environ["UPLOAD_AUTH_KEY"], prediction)


if __name__ == "__main__":
    main()
