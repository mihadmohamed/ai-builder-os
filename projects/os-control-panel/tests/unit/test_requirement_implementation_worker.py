from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


TOOLS_ROOT = Path(__file__).resolve().parents[2] / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import run_requirement_implementation as worker
from executor_continuity import CodexAvailability, RETRY_EXIT_CODE


class RequirementImplementationWorkerTests(unittest.TestCase):
    def test_worker_adds_repository_root_for_project_registry_imports(self) -> None:
        self.assertIn(str(worker.REPO_ROOT), sys.path)

    def test_worker_starts_with_the_minimal_supervisor_import_environment(self) -> None:
        result = subprocess.run(
            [sys.executable, str(TOOLS_ROOT / "run_requirement_implementation.py"), "--help"],
            env={
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": os.pathsep.join((str(worker.SRC_ROOT), str(worker.REPO_ROOT))),
            },
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--attempt-id", result.stdout)

    def test_codex_execution_refreshes_heartbeat_until_process_finishes(self) -> None:
        process = SimpleNamespace(returncode=0)
        process.communicate = unittest.mock.Mock(
            side_effect=[
                subprocess.TimeoutExpired(["codex", "exec"], 30),
                ("done", ""),
            ]
        )

        with (
            patch.object(worker.subprocess, "Popen", return_value=process),
            patch.object(worker, "update_implementation_run") as update_run,
        ):
            result = worker._run_codex_with_heartbeat(
                ["codex", "exec"],
                cwd=Path("/tmp"),
                run_id="run-1",
                attempt_id="attempt-1",
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "done")
        self.assertEqual(update_run.call_args.kwargs["run_id"] if "run_id" in update_run.call_args.kwargs else update_run.call_args.args[0], "run-1")
        self.assertTrue(update_run.call_args.kwargs["heartbeat_at"])

    def test_authoritative_usage_rejection_returns_to_waiting(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            run = SimpleNamespace(
                run_id="run-1",
                output_path=str(Path(temporary) / "output.txt"),
                started_at="",
                attempt_id="attempt-1",
                attempt_count=0,
                project_name="demo",
                requirement_id="R1",
                status="QUEUED",
                queue_request_id="queue-1",
            )
            availability = CodexAvailability(available=True, observed_at="2026-08-31T00:00:00+00:00")
            client = SimpleNamespace(availability=lambda: availability)
            packet = SimpleNamespace(
                run_id="controller-1",
                lease_token="private",
                claimed_at="2026-08-31T00:00:00+00:00",
                expires_at="2026-08-31T02:00:00+00:00",
                tasks=({"number": 1},),
            )
            controller = SimpleNamespace(
                prepare_managed_implementation_attempt=lambda *args: {"state": "READY_FOR_FRESH_CLAIM"},
                claim_implementation=lambda *args, **kwargs: packet,
                suspend_implementation_claim=unittest.mock.Mock(),
            )
            result = subprocess.CompletedProcess(
                ["codex", "exec"],
                1,
                stdout="",
                stderr="Usage limit reached; resets in one hour.",
            )

            with (
                patch.object(sys, "argv", ["worker", "--run-id", "run-1", "--project-name", "demo", "--requirement-id", "R1", "--attempt-id", "attempt-1"]),
                patch.object(worker, "list_implementation_runs", return_value=[run]),
                patch.object(worker, "CodexAppServerClient", return_value=client),
                patch.object(worker, "update_implementation_run", return_value=run),
                patch.object(worker, "build_requirement_implementation_prompt", return_value="prompt"),
                patch.object(worker, "_resolve_codex_executable", return_value=Path("/tmp/codex")),
                patch.object(worker, "resolve_project", return_value=SimpleNamespace(workspace_path=Path(temporary))),
                patch.object(worker, "_run_codex_with_heartbeat", return_value=result),
                patch.object(worker, "mark_implementation_waiting", return_value=run) as mark_waiting,
                patch.object(worker, "WorkflowController", return_value=controller),
            ):
                exit_code = worker.main()

        self.assertEqual(exit_code, RETRY_EXIT_CODE)
        self.assertIn("became temporarily unavailable", mark_waiting.call_args.kwargs["reason"])
        self.assertEqual(mark_waiting.call_args.kwargs["exit_code"], 1)
        controller.suspend_implementation_claim.assert_called_once()

    def test_managed_worker_uses_jsonl_and_explicit_workspace_write_sandbox(self) -> None:
        source = (TOOLS_ROOT / "run_requirement_implementation.py").read_text(encoding="utf-8")
        self.assertIn('"--json"', source)
        self.assertIn('"--sandbox",', source)
        self.assertIn('"workspace-write"', source)


if __name__ == "__main__":
    unittest.main()
