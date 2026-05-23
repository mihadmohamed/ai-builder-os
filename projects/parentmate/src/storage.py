import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FILE = DATA_DIR / "events.json"

def save_event(data):
    print(">>> SAVING EVENT <<<", data)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if FILE.exists():
        existing = json.loads(FILE.read_text())
    else:
        existing = []

    existing.append(data)
    FILE.write_text(json.dumps(existing, indent=2))

def load_events():
    if not FILE.exists():
        return []
    return json.loads(FILE.read_text())
