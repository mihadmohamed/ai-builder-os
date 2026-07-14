from __future__ import annotations

import hashlib
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import fcntl


REPO_ROOT = Path(__file__).resolve().parents[4]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_path(project_name: str) -> Path:
    if not project_name or project_name in {".", ".."} or "/" in project_name or "\\" in project_name:
        raise ValueError("project_name must be a direct child of projects/")
    path = (REPO_ROOT / "projects" / project_name).resolve()
    projects_root = (REPO_ROOT / "projects").resolve()
    if path.parent != projects_root or not path.is_dir():
        raise ValueError(f"Unknown project: {project_name}")
    return path


def runtime_root() -> Path:
    configured = os.getenv("AI_BUILDER_OS_RUNTIME_ROOT", "").strip()
    return Path(configured).expanduser().resolve() if configured else REPO_ROOT


def control_data_dir(project_name: str) -> Path:
    project_path(project_name)
    path = runtime_root() / "projects" / project_name / "data" / "control_plane"
    path.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def project_lock(project_name: str) -> Iterator[None]:
    lock_path = control_data_dir(project_name) / "controller.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def append_history(project_name: str, event: dict[str, Any]) -> dict[str, Any]:
    path = project_path(project_name) / "product" / "history.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = {"recorded_at": utc_now(), **event}
    line = json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n"
    with project_lock(project_name):
        idempotency_key = str(event.get("idempotency_key", ""))
        if idempotency_key and path.exists():
            for existing_line in reversed(path.read_text(encoding="utf-8").splitlines()):
                existing = json.loads(existing_line)
                if existing.get("idempotency_key") == idempotency_key:
                    return existing
        with path.open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
    return normalized


def read_history(project_name: str, *, limit: int = 50) -> list[dict[str, Any]]:
    path = project_path(project_name) / "product" / "history.jsonl"
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines[-max(0, limit) :] if line.strip()]


def sha256_file(path: Path) -> str:
    if not path.exists():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()
