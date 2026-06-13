import json
import os
from pathlib import Path

RUNTIME_ROOT_ENV = "AI_BUILDER_OS_RUNTIME_ROOT"
REPO_ROOT = Path(__file__).resolve().parents[3]


def _runtime_root() -> Path:
    raw = os.getenv(RUNTIME_ROOT_ENV, "").strip()
    if not raw:
        return REPO_ROOT
    return Path(raw).expanduser().resolve()


DATA_DIR = _runtime_root() / "projects" / "parentmate" / "data"
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
