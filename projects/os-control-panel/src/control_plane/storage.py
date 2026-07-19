from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

import fcntl

from tools.project_registry import resolve_project


REPO_ROOT = Path(__file__).resolve().parents[4]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def project_path(project_name: str) -> Path:
    return resolve_project(project_name).workspace_path


def project_id(project_name: str) -> str:
    return resolve_project(project_name).project_id


def runtime_root() -> Path:
    configured = os.getenv("AI_BUILDER_OS_RUNTIME_ROOT", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    home = os.getenv("AI_BUILDER_OS_HOME", "").strip()
    base = Path(home).expanduser().resolve() if home else REPO_ROOT / "private" / "ai-builder-os"
    return base / "runtime"


def control_data_dir(project_name: str) -> Path:
    location = resolve_project(project_name)
    path = runtime_root() / "projects" / location.project_id / "data" / "control_plane"
    legacy = runtime_root() / "projects" / location.name / "data" / "control_plane"
    if not path.exists() and legacy.exists() and legacy != path:
        shutil.copytree(legacy, path, dirs_exist_ok=True)
    repository_legacy = location.workspace_path / "data" / "control_plane"
    if not path.exists() and repository_legacy.exists():
        shutil.copytree(repository_legacy, path, dirs_exist_ok=True)
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


def atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(value)
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
