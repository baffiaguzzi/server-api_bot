import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def log_request(data: dict):
    now = datetime.now()
    logfile = LOG_DIR / f"requests_{now.strftime('%Y-%m')}.json"

    entry = {
        "timestamp": now.isoformat(),
        **data
    }

    if logfile.exists():
        content = json.loads(logfile.read_text(encoding="utf-8"))
    else:
        content = []

    content.append(entry)

    logfile.write_text(
        json.dumps(content, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
