from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parents[2] / "tools" / "manage_execution_supervisor.py"
SPEC = importlib.util.spec_from_file_location("manage_execution_supervisor", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExecutionSupervisorPackagingTests(unittest.TestCase):
    def test_launch_agent_is_per_user_minimal_and_restartable(self) -> None:
        payload = MODULE.launch_agent_payload()

        self.assertEqual(payload["Label"], "com.openai.ai-builder-os.execution-supervisor")
        self.assertTrue(payload["RunAtLoad"])
        self.assertTrue(payload["KeepAlive"])
        self.assertEqual(payload["ProcessType"], "Background")
        self.assertEqual(payload["StandardOutPath"], "/dev/null")
        self.assertEqual(payload["StandardErrorPath"], "/dev/null")
        self.assertIn("execution_supervisor.py", " ".join(payload["ProgramArguments"]))
        self.assertEqual(
            set(payload["EnvironmentVariables"]),
            {"PYTHONPATH", "AI_BUILDER_OS_RUNTIME_ROOT"},
        )
        rendered = repr(payload).casefold()
        self.assertNotIn("lease_token", rendered)
        self.assertNotIn("api_key", rendered)
        self.assertNotIn("launchdaemon", rendered)

    def test_supervisor_reconciles_before_scanning_retryable_runs(self) -> None:
        supervisor_path = Path(__file__).resolve().parents[2] / "tools" / "execution_supervisor.py"
        spec = importlib.util.spec_from_file_location("execution_supervisor_for_test", supervisor_path)
        assert spec is not None and spec.loader is not None
        supervisor = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(supervisor)

        with (
            patch.object(supervisor.os, "waitpid", side_effect=ChildProcessError),
            patch.object(supervisor, "reconcile_implementation_runs") as reconcile,
            patch.object(supervisor, "list_implementation_runs", return_value=[]),
        ):
            self.assertEqual(supervisor.supervise_once(), 0)

        reconcile.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
