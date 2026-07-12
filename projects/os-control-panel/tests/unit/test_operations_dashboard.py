from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import app  # noqa: E402
import operations_dashboard  # noqa: E402
import workspace  # noqa: E402


class OperationsDashboardTests(unittest.TestCase):
    def test_trace_summarizer_handles_completed_hand_back_and_legacy_runs(self) -> None:
        traces = {
            "alpha": [
                {
                    "trace_id": "complete",
                    "event": "run_started",
                    "role": "PM",
                    "model": "test",
                    "timestamp": "2026-06-06T10:00:00+00:00",
                },
                {
                    "trace_id": "complete",
                    "event": "model_call",
                    "role": "PM",
                    "attempt": 1,
                    "step": 1,
                    "timestamp": "2026-06-06T10:00:01+00:00",
                },
                {
                    "trace_id": "complete",
                    "event": "tool_completed",
                    "role": "PM",
                    "tool": "read_tasks",
                    "timestamp": "2026-06-06T10:00:02+00:00",
                },
                {
                    "trace_id": "complete",
                    "event": "run_completed",
                    "role": "PM",
                    "attempts": 1,
                    "steps": 2,
                    "tools": ["read_tasks"],
                    "guardrails": [{"kind": "sensitive_data"}],
                    "timestamp": "2026-06-06T10:00:05+00:00",
                },
                {
                    "trace_id": "hand-back",
                    "event": "run_started",
                    "role": "Orchestrator",
                    "timestamp": "2026-06-06T11:00:00+00:00",
                },
                {
                    "trace_id": "hand-back",
                    "event": "human_hand_back",
                    "role": "Orchestrator",
                    "reason": "Needs human review.",
                    "timestamp": "2026-06-06T11:00:01+00:00",
                },
                {
                    "trace_id": "legacy",
                    "event": "run_started",
                    "role": "Learning Agent",
                    "timestamp": "2026-06-06T09:00:00+00:00",
                },
                {
                    "trace_id": "legacy",
                    "event": "run_completed",
                    "role": "Learning Agent",
                    "attempts": 1,
                    "steps": 1,
                    "tools": [],
                    "timestamp": "2026-06-06T09:00:03+00:00",
                },
            ]
        }

        runs = operations_dashboard.summarize_agent_runs(traces)
        by_id = {run.trace_id: run for run in runs}

        self.assertEqual(by_id["complete"].status, "completed")
        self.assertEqual(by_id["complete"].duration_seconds, 5.0)
        self.assertEqual(by_id["complete"].tools, ("read_tasks",))
        self.assertEqual(by_id["complete"].guardrail_count, 1)
        self.assertEqual(by_id["hand-back"].status, "hand_back")
        self.assertEqual(by_id["hand-back"].hand_back_reason, "Needs human review.")
        self.assertEqual(by_id["legacy"].status, "completed")

    def test_role_performance_calculates_completion_and_retry_signals(self) -> None:
        runs = [
            operations_dashboard.AgentRunSummary(
                "1", "alpha", "PM", "test", "completed", "", "", None, 1, 1, (), 0, 0, ""
            ),
            operations_dashboard.AgentRunSummary(
                "2", "alpha", "PM", "test", "hand_back", "", "", None, 2, 2, ("read_tasks",), 1, 1, "Review"
            ),
        ]

        performance = operations_dashboard.summarize_role_performance(runs)[0]

        self.assertEqual(performance.total_runs, 2)
        self.assertEqual(performance.completion_rate, 50)
        self.assertEqual(performance.hand_backs, 1)
        self.assertEqual(performance.average_attempts, 1.5)
        self.assertEqual(performance.tool_calls, 1)

    def test_role_performance_keeps_complete_roster_without_live_runs(self) -> None:
        performance = operations_dashboard.summarize_role_performance(
            [],
            role_modes=operations_dashboard.AGENT_ROLE_MODES,
        )
        by_role = {item.role: item for item in performance}

        self.assertEqual(set(by_role), set(operations_dashboard.AGENT_ROLE_MODES))
        self.assertEqual(by_role["PM"].evidence_status, "No captured live runs")
        self.assertEqual(by_role["Experience Designer"].execution_mode, "Bounded live agent")
        self.assertEqual(by_role["Architect"].evidence_status, "Uses separate validation path")
        self.assertEqual(by_role["Engineer"].total_runs, 0)

    def test_tool_usage_includes_called_denied_and_unused_tools(self) -> None:
        usage = operations_dashboard.summarize_tool_usage(
            {
                "alpha": [
                    {
                        "trace_id": "1",
                        "event": "tool_completed",
                        "role": "PM",
                        "tool": "read_tasks",
                    },
                    {
                        "trace_id": "2",
                        "event": "human_hand_back",
                        "role": "PM",
                        "tool": "write_product_state",
                    },
                ]
            }
        )
        by_name = {item.tool_name: item for item in usage}

        self.assertEqual(by_name["read_tasks"].calls, 1)
        self.assertEqual(by_name["read_tasks"].roles, ("PM",))
        self.assertEqual(by_name["write_product_state"].denied_or_failed, 1)
        self.assertEqual(by_name["read_project_memory"].calls, 0)

    def test_operations_navigation_and_dashboard_views_are_exposed(self) -> None:
        self.assertIn("Operations", app.top_level_tab_labels())
        self.assertEqual(app.TOP_LEVEL_NAVIGATION_DESCRIPTIONS["Operations"], "Agent and workflow health")
        source = Path(app.__file__).read_text(encoding="utf-8")
        for label in (
            "Agent Operations",
            "Agent Quality",
            "Eval Coverage",
            "Workflow Health",
            "Human Oversight",
            "Agent Performance",
            "Tool Usage",
            "Learning Progress",
            "System Activity",
        ):
            self.assertIn(label, source)

    def test_operations_boards_explain_their_purpose_and_columns(self) -> None:
        source = Path(app.__file__).read_text(encoding="utf-8")
        for description_fragment in (
            "Shows individual live-agent runs",
            "Shows whether captured agent traces",
            "Roles remain visible even before they produce live traces",
            "Shows which evaluation types are implemented",
            "Shows the delivery and decision state",
            "Shows where human judgment is still required",
            "Compares captured run performance",
            "Shows which runtime tools exist",
            "Shows concept progression",
            "Combines live-agent runs and file-backed workflow events",
            "Inspect eval cases",
            "View full case payload",
        ):
            self.assertIn(description_fragment, source)

        config = app._operations_column_config(
            {
                "Project": "The project represented by this row.",
                "Status": "The recorded outcome.",
            }
        )
        self.assertEqual(config["Project"]["help"], "The project represented by this row.")
        self.assertEqual(config["Status"]["help"], "The recorded outcome.")

    def test_workspace_snapshot_joins_workflow_quality_and_learning_state(self) -> None:
        project = workspace.ProjectSummary(
            name="alpha",
            path=Path("/tmp/alpha"),
            structure_ok=True,
            missing_paths=(),
            default_ui_runtime="streamlit",
            requirement_counts={"NEW": 1, "IN_PROGRESS": 2, "BACKLOG": 3},
            new_requirements=(),
            task_counts={"TODO": 2},
            pending_tasks=(
                workspace.TaskSummary(id="1", title="One", status="TODO"),
                workspace.TaskSummary(id="2", title="Two", status="TODO"),
            ),
        )
        inbox = [
            workspace.InboxItem("clarification", "Blocked", "", "alpha", "blocked", "1", ""),
            workspace.InboxItem("finding", "Routed", "", "alpha", "routed", "2", ""),
        ]
        review = SimpleNamespace(status="PASS")
        with patch("workspace.load_agent_traces", return_value=[]), patch(
            "workspace.workflow_inbox_items", return_value=inbox
        ), patch("workspace.active_approvals", return_value=[]), patch(
            "workspace.active_pm_clarifications", return_value=[]
        ), patch("workspace.list_implementation_runs", return_value=[]), patch(
            "workspace.latest_quality_review", return_value=review
        ), patch("workspace.workflow_timeline_events", return_value=[]), patch(
            "workspace.learning_progress_items",
            return_value={"learned": [], "in_progress": [], "upcoming": []},
        ), patch("workspace.load_learning_agent_session", return_value=None):
            snapshot = workspace.operations_dashboard_snapshot([project])

        health = snapshot.workflow_health[0]
        self.assertEqual(health.pending_tasks, 2)
        self.assertEqual(health.blocked_items, 1)
        self.assertEqual(health.routed_items, 1)
        self.assertEqual(health.quality_status, "PASS")
        self.assertIn("write_product_state", snapshot.high_risk_tools)
        self.assertIn("publish_to_github", snapshot.high_risk_tools)


if __name__ == "__main__":
    unittest.main()
