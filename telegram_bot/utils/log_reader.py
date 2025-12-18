import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

LOG_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR = Path(__file__).resolve().parent.parent.parent / "logs"


def read_latest_logs(limit=5):
    if not LOG_DIR.exists():
        return []

    files = sorted(LOG_DIR.glob("requests_*.json"), reverse=True)

    entries = []
    for file in files:
        data = json.loads(file.read_text(encoding="utf-8"))
        entries.extend(reversed(data))
        if len(entries) >= limit:
            break

    return entries[:limit]


def get_latest_logfile():
    files = sorted(LOG_DIR.glob("requests_*.json"), reverse=True)
    return files[0] if files else None


def compute_stats_for_month(year: int | None = None, month: int | None = None) -> dict:
    """
    Read the monthly JSON file (ex: logs/2025-12.json) and create the stats per endpoint.
    Returns a dict with:
        - total_requests
        - per_endpoint: {endpoint_name: {...}}
    """
    year = year or datetime.now().year
    month = month or datetime.now().month
    fname = f"{year:04d}-{month:02d}.json"
    log_file = LOGS_DIR / fname
    if not log_file.exists():
        return {"total_requests": 0, "per_endpoint": {}}

    try:
        data = json.loads(log_file.read_text(encoding="utf-8"))
    except Exception:
        return {"total_requests": 0, "per_endpoint": {}}

    per_ep = defaultdict(lambda: {
        "count": 0,
        "ok": 0,
        "warn": 0,
        "err": 0,
        "total_time_ms": 0.0,
    })

    for entry in data:
        ep = entry.get("endpoint", "UNKNOWN")
        label = entry.get("status_label", "ERR")
        time_ms = entry.get("time_ms") or 0
        per_ep[ep]["count"] += 1
        per_ep[ep]["total_time_ms"] += time_ms

        if label == "OK":
            per_ep[ep]["ok"] += 1
        elif label == "WARN":
            per_ep[ep]["warn"] += 1
        else:
            per_ep[ep]["err"] += 1

    return {
        "total_requests": sum(v["count"] for v in per_ep.values()),
        "per_endpoint": per_ep,
    }
