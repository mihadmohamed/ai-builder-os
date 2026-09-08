from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import socket
import subprocess
import sys
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from workspace import (  # noqa: E402
    build_requirement_implementation_prompt,
    list_implementation_runs,
    load_project_ui_runtime,
    mark_implementation_waiting,
    project_runtime_profile,
    reconcile_web_app_requirement_after_verification,
    update_implementation_run,
    _resolve_codex_executable,
)
from executor_continuity import (  # noqa: E402
    RETRY_EXIT_CODE,
    CodexAppServerClient,
    CodexAppServerError,
    classify_codex_failure,
    parse_managed_completion_report,
    parse_codex_exec_jsonl,
    safe_error,
)
from control_plane.service import WorkflowController  # noqa: E402
from control_plane.storage import sha256_file  # noqa: E402
from tools.project_registry import resolve_project  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a background Codex implementation flow for one requirement.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--requirement-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    return parser


def _read_output(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text().strip()


def _available_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _run_web_app_verification(project_name: str, requirement_id: str) -> tuple[bool, str]:
    port = _available_local_port()
    command = [
        sys.executable,
        str(REPO_ROOT / "tools" / "verify_web_app.py"),
        project_name,
        "--port",
        str(port),
    ]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or result.stderr or "").strip()
    if result.returncode != 0:
        return False, output or "Web app browser verification failed."
    updated_tasks = reconcile_web_app_requirement_after_verification(project_name, requirement_id)
    note = "Web app browser verification passed."
    if updated_tasks:
        note += f" Marked {updated_tasks} validation task"
        if updated_tasks != 1:
            note += "s"
        note += " DONE."
    return True, "\n".join(part for part in (note, output) if part).strip()


def _run_codex_with_heartbeat(
    command: list[str], *, cwd: Path, run_id: str, attempt_id: str
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    while True:
        try:
            stdout, stderr = process.communicate(timeout=30)
            return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        except subprocess.TimeoutExpired:
            update_implementation_run(
                run_id,
                heartbeat_at=datetime.now(timezone.utc).isoformat(),
                expected_attempt_id=attempt_id,
                expected_statuses=("RUNNING",),
            )


def main() -> int:
    args = build_parser().parse_args()
    run = next((item for item in list_implementation_runs(args.project_name) if item.run_id == args.run_id), None)
    if run is None:
        raise ValueError(f"Implementation run not found: {args.run_id}")
    if (
        run.project_name != args.project_name
        or run.requirement_id != args.requirement_id
        or run.attempt_id != args.attempt_id
        or run.status != "QUEUED"
    ):
        raise ValueError("Managed worker arguments do not match the current queued attempt")

    try:
        availability = CodexAppServerClient().availability()
    except (CodexAppServerError, FileNotFoundError, OSError, subprocess.SubprocessError) as exc:
        mark_implementation_waiting(
            args.run_id,
            reason="Codex App Server is temporarily unavailable.",
            safe_detail=str(exc),
            app_server_status="unavailable",
            expected_attempt_id=args.attempt_id,
        )
        return RETRY_EXIT_CODE
    if not availability.available:
        mark_implementation_waiting(
            args.run_id,
            reason="Codex usage is temporarily unavailable.",
            availability=availability,
            expected_attempt_id=args.attempt_id,
        )
        return RETRY_EXIT_CODE

    started_at = datetime.now(timezone.utc).isoformat()
    attempt_id = args.attempt_id
    controller = WorkflowController()
    try:
        preparation = controller.prepare_managed_implementation_attempt(
            args.project_name, args.run_id, attempt_id
        )
    except Exception as exc:
        detail = safe_error(str(exc))
        update_implementation_run(
            args.run_id,
            status="FAILED",
            error=detail,
            last_safe_error=detail,
            finished_at=started_at,
            event=("managed_attempt_gate_failed", {}),
            expected_attempt_id=attempt_id,
            expected_statuses=("QUEUED",),
            clear_worker_pid=True,
        )
        return 1
    if preparation["state"] == "TERMINAL_EVIDENCE":
        terminal_status = str(preparation["status"])
        terminal_summary = str(preparation.get("summary", ""))
        update_implementation_run(
            args.run_id,
            status=terminal_status,
            summary=terminal_summary,
            error=terminal_summary if terminal_status != "COMPLETED" else "",
            finished_at=started_at,
            event=("controller_terminal_evidence_reconciled", {}),
            expected_attempt_id=attempt_id,
            expected_statuses=("QUEUED",),
            clear_worker_pid=True,
        )
        if run.queue_request_id:
            controller.resolve_codex_work_request(
                args.project_name,
                run.queue_request_id,
                actor="managed_codex_exec",
                status=terminal_status,
                summary=terminal_summary,
                implementation_run_id=str(preparation.get("controller_run_id", "")),
            )
        return 0 if terminal_status == "COMPLETED" else 1
    try:
        packet = controller.claim_implementation(
            args.project_name,
            args.requirement_id,
            executor="managed_codex_exec",
            idempotency_key=f"managed-attempt:{run.run_id}:{attempt_id}",
        )
    except Exception as exc:
        detail = safe_error(str(exc))
        update_implementation_run(
            args.run_id,
            status="FAILED",
            error=detail,
            last_safe_error=detail,
            finished_at=datetime.now(timezone.utc).isoformat(),
            event=("fresh_authority_failed", {}),
            expected_attempt_id=attempt_id,
            expected_statuses=("QUEUED",),
        )
        return 1
    run = update_implementation_run(
        args.run_id,
        status="RUNNING",
        started_at=run.started_at or started_at,
        attempt_count=run.attempt_count + 1,
        last_attempt_at=started_at,
        attempt_id=attempt_id,
        attempt_started_at=started_at,
        heartbeat_at=started_at,
        app_server_status="healthy",
        availability=availability.to_dict(),
        observed_at=availability.observed_at,
        event=("executor_attempt_started", {"attempt_id": attempt_id}),
        controller_run_id=packet.run_id,
        authorization_claimed_at=packet.claimed_at,
        authorization_expires_at=packet.expires_at,
        expected_attempt_id=attempt_id,
        expected_statuses=("QUEUED",),
    )

    output_path = Path(run.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.touch(exist_ok=True)
    try:
        output_path.parent.chmod(0o700)
        output_path.chmod(0o600)
    except OSError:
        pass
    prompt = build_requirement_implementation_prompt(args.project_name, args.requirement_id, run) + (
        "\nThe managed wrapper already acquired the fresh bounded controller claim for this attempt; "
        "do not claim or close controller state yourself. End with only one JSON object containing exactly "
        "summary, files_changed (project-relative paths), tests (bounded result strings), and "
        "completed_task_numbers (only task numbers from the claimed packet)."
    )
    target_root = resolve_project(args.project_name).workspace_path

    try:
        codex_executable = _resolve_codex_executable()
        result = _run_codex_with_heartbeat(
            [
                str(codex_executable),
                "exec",
                "--json",
                "--sandbox",
                "workspace-write",
                "--approve-for-me",
                "--skip-git-repo-check",
                "--color",
                "never",
                "-C",
                str(target_root),
                "-o",
                str(output_path),
                prompt,
            ],
            cwd=target_root,
            run_id=args.run_id,
            attempt_id=attempt_id,
        )
    except Exception as exc:
        detail = safe_error(str(exc))
        try:
            controller.record_implementation_evidence(
                args.project_name,
                packet.run_id,
                packet.lease_token,
                summary=detail,
                files_changed=[],
                tests=[],
                status="FAILED",
            )
        except Exception:
            pass
        update_implementation_run(
            args.run_id,
            status="FAILED",
            error=detail,
            last_safe_error=detail,
            finished_at=datetime.now(timezone.utc).isoformat(),
            event=("executor_attempt_failed", {"category": "worker_exception"}),
            expected_attempt_id=attempt_id,
            expected_statuses=("RUNNING",),
            clear_worker_pid=True,
        )
        return 1

    summary = _read_output(output_path)
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    finished_at = datetime.now(timezone.utc).isoformat()
    try:
        observation = parse_codex_exec_jsonl(stdout)
    except ValueError:
        observation = None
    if observation is not None:
        attempt = {"executor": "codex", **observation.to_dict()}
        run = update_implementation_run(
            args.run_id,
            executor_policy_version="r120-observation-v1",
            executor_attempts=(*getattr(run, "executor_attempts", ()), attempt),
            event=("codex_exec_jsonl_observed", {"terminal_status": observation.terminal_status}),
            expected_attempt_id=attempt_id,
            expected_statuses=("RUNNING",),
        )

    if result.returncode != 0:
        error_parts = [part for part in [stderr, observation.safe_error if observation else "", stdout] if part]
        classification = classify_codex_failure(
            exit_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
        )
        if classification.retryable:
            try:
                refreshed = CodexAppServerClient().availability()
            except (CodexAppServerError, FileNotFoundError, OSError, subprocess.SubprocessError):
                refreshed = None
            # Release bounded authority before publishing reusable waiting state.
            controller.suspend_implementation_claim(
                args.project_name,
                packet.run_id,
                packet.lease_token,
                reason=classification.safe_error,
            )
            mark_implementation_waiting(
                args.run_id,
                reason="Codex usage became temporarily unavailable during execution.",
                availability=refreshed,
                exit_code=result.returncode,
                safe_detail=classification.safe_error,
                app_server_status="healthy" if refreshed is not None else "unavailable",
                expected_attempt_id=attempt_id,
            )
            return RETRY_EXIT_CODE
        try:
            controller.record_implementation_evidence(
                args.project_name,
                packet.run_id,
                packet.lease_token,
                summary=classification.safe_error,
                files_changed=[],
                tests=[],
                status="FAILED",
            )
            if run.queue_request_id:
                controller.resolve_codex_work_request(
                    args.project_name,
                    run.queue_request_id,
                    actor="managed_codex_exec",
                    status="FAILED",
                    summary=classification.safe_error,
                    implementation_run_id=packet.run_id,
                )
        except Exception:
            pass
        update_implementation_run(
            args.run_id,
            status="FAILED",
            summary=summary,
            error=classification.safe_error,
            last_exit_code=result.returncode,
            last_safe_error=classification.safe_error,
            finished_at=finished_at,
            event=("executor_attempt_failed", {"category": classification.category}),
            expected_attempt_id=attempt_id,
            expected_statuses=("RUNNING",),
            clear_worker_pid=True,
        )
        return result.returncode

    try:
        report = parse_managed_completion_report(
            summary,
            workspace_root=target_root,
            allowed_task_numbers=(int(item["number"]) for item in packet.tasks),
        )
    except (ValueError, TypeError, KeyError) as exc:
        detail = safe_error(str(exc))
        controller.record_implementation_evidence(
            args.project_name,
            packet.run_id,
            packet.lease_token,
            summary=detail,
            files_changed=[],
            tests=[],
            status="FAILED",
        )
        update_implementation_run(
            args.run_id,
            status="FAILED",
            error=detail,
            last_safe_error=detail,
            finished_at=finished_at,
            event=("completion_report_rejected", {}),
            expected_attempt_id=attempt_id,
            expected_statuses=("RUNNING",),
            clear_worker_pid=True,
        )
        return 1

    runtime = project_runtime_profile(load_project_ui_runtime(args.project_name))
    if runtime.runtime == "web_app":
        verification_ok, verification_detail = _run_web_app_verification(args.project_name, args.requirement_id)
        if not verification_ok:
            combined_summary = "\n\n".join(part for part in (report.summary, verification_detail) if part).strip()
            controller.record_implementation_evidence(
                args.project_name,
                packet.run_id,
                packet.lease_token,
                summary=combined_summary,
                files_changed=list(report.files_changed),
                tests=[*report.tests, verification_detail],
                status="FAILED",
            )
            update_implementation_run(
                args.run_id,
                status="FAILED",
                summary=combined_summary,
                error=verification_detail or "Web app browser verification failed.",
                finished_at=datetime.now(timezone.utc).isoformat(),
                expected_attempt_id=attempt_id,
                expected_statuses=("RUNNING",),
                clear_worker_pid=True,
            )
            return 1
        report = type(report)(
            summary="\n\n".join((report.summary, verification_detail)).strip(),
            files_changed=report.files_changed,
            tests=(*report.tests, verification_detail),
            completed_task_numbers=report.completed_task_numbers,
        )

    controller.record_implementation_evidence(
        args.project_name,
        packet.run_id,
        packet.lease_token,
        summary=report.summary,
        files_changed=list(report.files_changed),
        tests=list(report.tests),
        status="COMPLETED",
        completed_task_numbers=list(report.completed_task_numbers),
        source_requirements_sha256=sha256_file(target_root / "product" / "requirements.md"),
        source_tasks_sha256=sha256_file(target_root / "product" / "tasks.md"),
    )

    update_implementation_run(
        args.run_id,
        status="COMPLETED",
        summary=report.summary,
        error="",
        finished_at=finished_at,
        heartbeat_at=finished_at,
        event=("executor_attempt_completed", {"attempt_id": attempt_id}),
        expected_attempt_id=attempt_id,
        expected_statuses=("RUNNING",),
        clear_worker_pid=True,
    )
    if run.queue_request_id:
        controller.resolve_codex_work_request(
            args.project_name,
            run.queue_request_id,
            actor="managed_codex_exec",
            status="COMPLETED",
            summary=report.summary,
            implementation_run_id=packet.run_id,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
