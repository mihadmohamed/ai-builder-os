from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from executor_continuity import WAITING_FOR_EXECUTOR, eligibility_due, safe_error  # noqa: E402
from workspace import (  # noqa: E402
    list_implementation_runs,
    reconcile_implementation_runs,
    retry_waiting_implementation,
)


MAX_LOG_BYTES = 65_536
MAX_LOG_EVENTS = 200


def _event_log_path() -> Path:
    configured = os.getenv("AI_BUILDER_OS_RUNTIME_ROOT", "").strip()
    root = Path(configured).expanduser() if configured else PROJECT_ROOT.parents[1] / "private" / "ai-builder-os" / "runtime"
    return root / "supervisor" / "events.jsonl"


def _record_event(event: str, *, run_id: str = "", detail: str = "") -> None:
    path = _event_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8", errors="replace").splitlines() if path.exists() else []
    payload = {
        "event": event,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "detail": safe_error(detail),
    }
    lines = [*existing[-(MAX_LOG_EVENTS - 1):], json.dumps(payload, separators=(",", ":"))]
    while len("\n".join(lines).encode("utf-8")) > MAX_LOG_BYTES and len(lines) > 1:
        lines.pop(0)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        path.parent.chmod(0o700)
        path.chmod(0o600)
    except OSError:
        pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resume eligible implementation runs after temporary Codex executor limits."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="Check eligible runs once and exit (default).")
    mode.add_argument("--loop", action="store_true", help="Keep checking until stopped.")
    parser.add_argument("--interval-seconds", type=int, default=60)
    return parser


def supervise_once() -> int:
    # Reap detached workers started by this process, then reconcile their
    # durable state before considering waiting retries.  This prevents a dead
    # process (including a zombie) from leaving a run indefinitely queued.
    while True:
        try:
            child_pid, _ = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            break
        if child_pid <= 0:
            break
    reconcile_implementation_runs()
    now = datetime.now(timezone.utc)
    resumed = 0
    for run in list_implementation_runs():
        if run.status != WAITING_FOR_EXECUTOR or not eligibility_due(run.retry_after, now=now):
            continue
        try:
            updated = retry_waiting_implementation(run.run_id)
        except Exception as exc:
            _record_event("supervisor_check_failed", run_id=run.run_id, detail=str(exc))
            continue
        if updated.status in {"QUEUED", "RUNNING"}:
            resumed += 1
            _record_event("executor_resumed", run_id=run.run_id)
    return resumed


def main() -> int:
    args = build_parser().parse_args()
    interval = max(15, min(args.interval_seconds, 3600))
    if not args.loop:
        supervise_once()
        return 0
    while True:
        try:
            supervise_once()
        except Exception as exc:
            _record_event("supervisor_cycle_failed", detail=str(exc))
        time.sleep(interval)


if __name__ == "__main__":
    raise SystemExit(main())
