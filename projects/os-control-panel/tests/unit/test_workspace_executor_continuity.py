from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace


import workspace
from executor_continuity import CodexAvailability, RateLimitWindow, WAITING_FOR_EXECUTOR


class WorkspaceExecutorContinuityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        self.store = root / "implementation_runs.json"
        self.logs = root / "logs"
        self.patches = (
            patch.object(workspace, "IMPLEMENTATION_FILE", self.store),
            patch.object(workspace, "IMPLEMENTATION_LOG_DIR", self.logs),
            patch.object(workspace, "project_lock", lambda _: nullcontext()),
        )
        for item in self.patches:
            item.start()

    def tearDown(self) -> None:
        for item in reversed(self.patches):
            item.stop()
        self.temporary.cleanup()

    def _write_run(self, status: str = "RUNNING") -> dict[str, object]:
        raw = {
            "run_id": "run-1",
            "project_name": "demo",
            "requirement_id": "R1",
            "requirement_title": "Continuity",
            "status": status,
            "summary": "",
            "error": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": "",
            "finished_at": "",
            "output_path": str(self.logs / "output.txt"),
            "log_path": str(self.logs / "run.log"),
            "worker_pid": 999,
            "attempt_count": 1,
            "attempt_id": "attempt-1",
            "attempt_version": 1,
            "events": [],
        }
        self.store.parent.mkdir(parents=True, exist_ok=True)
        self.store.write_text(json.dumps([raw]))
        return raw

    def test_wait_state_is_persisted_without_marking_run_finished(self) -> None:
        self._write_run()
        now = datetime.now(timezone.utc)
        availability = CodexAvailability(
            available=False,
            observed_at=now.isoformat(),
            primary=RateLimitWindow(
                identifier="primary",
                used_percent=100,
                resets_at=(now + timedelta(hours=1)).isoformat(),
                exhausted=True,
            ),
        )

        run = workspace.mark_implementation_waiting(
            "run-1",
            reason="Codex usage is temporarily unavailable.",
            availability=availability,
            exit_code=1,
            safe_detail="usage limit reached",
        )

        self.assertEqual(run.status, WAITING_FOR_EXECUTOR)
        self.assertEqual(run.finished_at, "")
        self.assertEqual(run.blocking_window_ids, ("primary",))
        self.assertEqual(run.retry_strategy, "reported_reset")
        self.assertEqual(run.events[-1]["event"], "executor_wait_started")

    def test_resume_claim_is_compare_and_swap(self) -> None:
        self._write_run(WAITING_FOR_EXECUTOR)
        record = workspace.RequirementRecord("R1", "Continuity", "IN_PROGRESS", "P0", "M", "")
        document = workspace.RequirementDocument("", (record,), (), "")

        with patch.object(workspace, "load_requirement_document", return_value=document):
            first = workspace.claim_waiting_implementation_resume("run-1")
            second = workspace.claim_waiting_implementation_resume("run-1")

        self.assertIsNotNone(first)
        self.assertEqual(first.status, "QUEUED")
        self.assertIsNone(second)

    def test_reconciliation_does_not_fail_a_waiting_run_without_worker(self) -> None:
        raw = self._write_run(WAITING_FOR_EXECUTOR)
        raw["worker_pid"] = None
        raw["created_at"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        self.store.write_text(json.dumps([raw]))

        runs = workspace.reconcile_implementation_runs("demo")

        self.assertEqual(runs[0].status, WAITING_FOR_EXECUTOR)

    def test_reconciliation_rejects_reused_worker_pid(self) -> None:
        raw = self._write_run("RUNNING")
        raw["heartbeat_at"] = datetime.now(timezone.utc).isoformat()
        self.store.write_text(json.dumps([raw]))

        with (
            patch.object(workspace, "_worker_process_alive", return_value=True),
            patch.object(workspace, "_worker_process_matches_run", return_value=False),
        ):
            runs = workspace.reconcile_implementation_runs("demo")

        self.assertEqual(runs[0].status, "FAILED")
        self.assertIn("identity or heartbeat", runs[0].error)

    def test_zombie_worker_is_not_considered_alive(self) -> None:
        with patch.object(
            workspace.subprocess,
            "run",
            return_value=SimpleNamespace(returncode=0, stdout="Z\n"),
        ):
            self.assertFalse(workspace._worker_process_alive(123))

    def test_spawned_worker_receives_only_required_import_roots(self) -> None:
        raw = self._write_run("QUEUED")
        run = workspace._implementation_run_from_dict(raw)
        process = SimpleNamespace(pid=321)

        with (
            patch.object(workspace, "_implementation_command", return_value=["worker"]),
            patch.object(workspace.subprocess, "Popen", return_value=process) as popen,
        ):
            workspace._spawn_implementation_worker(run)

        env = popen.call_args.kwargs["env"]
        self.assertEqual(
            env["PYTHONPATH"].split(workspace.os.pathsep),
            [str(workspace._project_path("os-control-panel") / "src"), str(workspace.REPO_ROOT)],
        )

    def test_recent_heartbeat_tolerates_denied_process_inspection(self) -> None:
        raw = self._write_run("RUNNING")
        raw["heartbeat_at"] = datetime.now(timezone.utc).isoformat()
        self.store.write_text(json.dumps([raw]))

        with (
            patch.object(workspace, "_worker_process_alive", return_value=True),
            patch.object(workspace, "_worker_process_matches_run", return_value=None),
        ):
            runs = workspace.reconcile_implementation_runs("demo")

        self.assertEqual(runs[0].status, "RUNNING")

    def test_unsafe_requirement_drift_blocks_resume(self) -> None:
        raw = self._write_run(WAITING_FOR_EXECUTOR)
        raw["requirement_fingerprint"] = "stale-fingerprint"
        self.store.write_text(json.dumps([raw]))
        record = workspace.RequirementRecord("R1", "Continuity", "IN_PROGRESS", "P0", "M", "")
        document = workspace.RequirementDocument("", (record,), (), "")

        with patch.object(workspace, "load_requirement_document", return_value=document):
            claimed = workspace.claim_waiting_implementation_resume("run-1")

        self.assertIsNone(claimed)
        self.assertEqual(workspace.list_implementation_runs()[0].status, "FAILED")

    def test_wait_persistence_never_adds_lease_material(self) -> None:
        self._write_run()
        workspace.mark_implementation_waiting("run-1", reason="App Server unavailable")

        persisted = self.store.read_text()

        self.assertNotIn("lease_token", persisted)
        self.assertNotIn("authorization_header", persisted)

    def test_stale_attempt_cannot_heartbeat_or_finish_newer_attempt(self) -> None:
        self._write_run("RUNNING")

        with self.assertRaisesRegex(RuntimeError, "Stale implementation attempt"):
            workspace.update_implementation_run(
                "run-1",
                heartbeat_at=datetime.now(timezone.utc).isoformat(),
                expected_attempt_id="attempt-old",
                expected_statuses=("RUNNING",),
            )

        current = workspace.list_implementation_runs()[0]
        self.assertEqual(current.attempt_id, "attempt-1")
        self.assertEqual(current.status, "RUNNING")

    def test_unavailable_app_server_persists_escalating_bounded_checks(self) -> None:
        self._write_run()
        first = workspace.mark_implementation_waiting("run-1", reason="App Server unavailable")
        second = workspace.mark_implementation_waiting("run-1", reason="App Server unavailable")

        first_retry = datetime.fromisoformat(first.retry_after)
        second_retry = datetime.fromisoformat(second.retry_after)
        self.assertEqual(first.retry_check_count, 1)
        self.assertEqual(second.retry_check_count, 2)
        self.assertGreater(second_retry - first_retry, timedelta(minutes=14))
        self.assertEqual(second.retry_strategy, "app_server_backoff_with_jitter")

    def test_preview_discovery_fails_closed_when_process_listing_is_denied(self) -> None:
        with patch.object(workspace.subprocess, "run", side_effect=PermissionError("denied")):
            self.assertEqual(workspace._candidate_web_app_preview_pids(), ())

    def test_fresh_resume_prompt_uses_canonical_state_and_no_lease_secret(self) -> None:
        raw = self._write_run(WAITING_FOR_EXECUTOR)
        raw.update(
            {
                "authorization_id": "sealed-auth",
                "queue_request_id": "queue-1",
                "controller_run_id": "controller-1",
            }
        )
        run = workspace._implementation_run_from_dict(raw)

        prompt = workspace.build_requirement_implementation_prompt("os-control-panel", "R118", run)

        self.assertIn("fresh execution context", prompt)
        self.assertIn("Re-read canonical requirements, tasks, history", prompt)
        self.assertIn("fresh bounded controller implementation claim", prompt)
        self.assertIn("sealed-auth", prompt)
        self.assertNotIn("lease_token", prompt)


if __name__ == "__main__":
    unittest.main()
