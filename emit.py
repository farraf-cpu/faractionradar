"""GHA emission wrapper — runs the predictor, POSTs to the calendar-worker,
writes a versioned .md report, and appends to predictions.jsonl.

Local dev: this is NOT for local runs. Use `python run.py` for that. This
script only makes sense when the GHA secrets are populated.

Environment (set by GHA workflow):
  FRED_API_KEY          — read by src/fred_fetch.py during the model run
  UPLOAD_AUTH_KEY       — used in POST body to authenticate to /upload
  CALENDAR_WORKER_URL   — e.g. https://faractionradar-calendar.faractionradar.workers.dev
  NFP_RELEASE_DATE      — ISO date of the NFP print this run is targeting (YYYY-MM-DD)
  NFP_DAYS_OUT          — integer: 7, 4, 3, 2, or 1 (which cadence slot)
  MODEL_VERSION         — pinned string, e.g. "v1-bayesian-blend"

Emits (all committed by the workflow after this script exits):
  reports/YYYY-MM/nfp-t-<N>.md      — full human-readable model output
  predictions.jsonl                  — one line per prediction, all-history ledger
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

REQUIRED_ENV = ["UPLOAD_AUTH_KEY", "CALENDAR_WORKER_URL", "NFP_RELEASE_DATE", "NFP_DAYS_OUT"]


def require_env(key: str) -> str:
    v = os.environ.get(key)
    if not v:
        print(f"[emit] missing required env var: {key}", file=sys.stderr)
        sys.exit(2)
    return v


def format_our_call(result: dict, release_date: str, model_version: str) -> dict:
    """Map the predictor's internal `result` dict to CalendarEvent.prediction.ourCall
    per ROADMAP §4.1. Model logic is untouched — this is pure shape mapping."""
    blended = result["blended"]
    rmse = result["blended_rmse"]
    return {
        "value": f"{blended:+.0f}K",
        "lean": result["lean"],
        "ci68": [round(blended - rmse), round(blended + rmse)],
        "ci95": [round(blended - 2 * rmse), round(blended + 2 * rmse)],
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "model_version": model_version,
    }


def format_grand_median(result: dict) -> dict:
    """7 sub-models feed the grand median — see docs/nfp-model-card.md."""
    return {
        "value": f"{result['grand_median']:+.0f}K",
        "sourceCount": 7,
    }


def build_report_md(result: dict, release_date: str, days_out: int, model_version: str) -> str:
    b = result["blended"]
    r = result["blended_rmse"]
    return f"""# NFP prediction — target {release_date} (T-{days_out})

**Model version:** `{model_version}`
**Published:** {datetime.now(timezone.utc).isoformat()}

## Final pick

**{b:+.0f}K jobs**

- 68% CI: [{b-r:+.0f}, {b+r:+.0f}] K
- 95% CI: [{b-2*r:+.0f}, {b+2*r:+.0f}] K
- Lean vs consensus: {result['lean']}

## Sub-model breakdown

| Sub-model | Value | Historical MAE |
|-----------|-------|----------------|
| Bloomberg consensus       | {result['consensus']:+7.0f} K | ~55 K |
| Prediction markets (avg)  | {result['pred_markets']:+7.0f} K | ~40 K |
| ML ensemble (revised)     | {result['ml_ensemble']:+7.0f} K | — |
| First-print ensemble      | {result['first_print_ensemble']:+7.0f} K | — |
| Bridge models median      | {result['bridge_median']:+7.0f} K | — |
| Sector decomposition (11) | {result['sector_pred']:+7.0f} K | — |
| Grand median (all models) | {result['grand_median']:+7.0f} K | — |
| **Blended (Bayesian)**    | **{b:+7.0f} K** | — |
"""


def append_ledger(payload: dict) -> None:
    """One JSON line per prediction. Append-only. Never rewrite."""
    ledger = ROOT / "predictions.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, separators=(",", ":")) + "\n")


def post_to_worker(url: str, auth_key: str, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "content-type": "application/json",
            "x-upload-auth": auth_key,
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"[emit] worker → {res.status} {res.reason}")
    except urllib.error.HTTPError as e:
        print(f"[emit] worker rejected: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(3)


def main() -> None:
    for key in REQUIRED_ENV:
        require_env(key)

    release_date = os.environ["NFP_RELEASE_DATE"]
    days_out = int(os.environ["NFP_DAYS_OUT"])
    model_version = os.environ.get("MODEL_VERSION", "v1-bayesian-blend")
    worker_url = os.environ["CALENDAR_WORKER_URL"].rstrip("/") + "/upload"
    auth_key = os.environ["UPLOAD_AUTH_KEY"]

    from run import main as run_predictor
    result = run_predictor(refresh_data=True)

    prediction = {
        "eventSlug": f"nfp-{release_date}",
        "eventTitle": "US Non-Farm Payrolls",
        "country": "USD",
        "releaseDate": release_date,
        "daysOut": days_out,
        "ourCall": format_our_call(result, release_date, model_version),
        "grandMedian": format_grand_median(result),
        "modelCardUrl": "https://github.com/farraf-cpu/faractionradar/blob/main/docs/nfp-model-card.md",
    }

    report_md = build_report_md(result, release_date, days_out, model_version)
    year_month = release_date[:7]
    report_path = ROOT / "reports" / year_month / f"nfp-t-{days_out}.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_md, encoding="utf-8")
    print(f"[emit] wrote {report_path.relative_to(ROOT)}")

    ledger_row = {
        "publishedAt": prediction["ourCall"]["publishedAt"],
        "eventSlug": prediction["eventSlug"],
        "daysOut": days_out,
        "modelVersion": model_version,
        "ourCall": prediction["ourCall"]["value"],
        "ci68": prediction["ourCall"]["ci68"],
        "grandMedian": prediction["grandMedian"]["value"],
        "reportPath": str(report_path.relative_to(ROOT)),
    }
    append_ledger(ledger_row)
    print(f"[emit] appended predictions.jsonl")

    post_to_worker(worker_url, auth_key, prediction)


if __name__ == "__main__":
    main()
