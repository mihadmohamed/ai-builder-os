from __future__ import annotations

import asyncio
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from codex_bridge.server import (
    NativeApprovalForm,
    decide_external_approval,
    resolve_agent_approval,
    start_agent_workflow,
)
from control_plane import WorkflowController
from workspace import ApprovalRequest


class FakeContext:
    def __init__(
        self,
        *,
        action: str = "accept",
        data: object = None,
        error: Exception | None = None,
    ) -> None:
        self.action = action
        self.data = data
        self.error = error
        self.messages: list[str] = []

    async def elicit(self, *, message: str, schema: object) -> object:
        self.messages.append(message)
        if self.error is not None:
            raise self.error
        return SimpleNamespace(action=self.action, data=self.data)


class NativeApprovalTests(unittest.TestCase):
    def test_api_start_fails_closed_until_exact_native_authorization(self) -> None:
        runtime = Mock()
        runtime.run.return_value = {"status": "COMPLETED"}
        cases = (
            (FakeContext(action="cancel"), "NOT_STARTED"),
            (FakeContext(error=RuntimeError("unsupported")), "FALLBACK_REQUIRED"),
            (
                FakeContext(data={"decision": "approve", "unexpected": "value"}),
                "NOT_STARTED",
            ),
            (FakeContext(data=NativeApprovalForm(decision="reject")), "NOT_STARTED"),
        )
        with patch("codex_bridge.server._agents_sdk_runtime", return_value=runtime):
            for context, expected in cases:
                result = asyncio.run(
                    start_agent_workflow(
                        context,
                        "demo",
                        "Do API work.",
                    )
                )
                self.assertEqual(result["status"], expected)
        runtime.run.assert_not_called()

        context = FakeContext(data=NativeApprovalForm(decision="approve"))
        with patch("codex_bridge.server._agents_sdk_runtime", return_value=runtime):
            result = asyncio.run(
                start_agent_workflow(
                    context,
                    "demo",
                    "Do API work.",
                    agent_name="orchestrator",
                )
            )
        self.assertEqual(result["status"], "COMPLETED")
        runtime.run.assert_called_once()
        self.assertEqual(
            runtime.run.call_args.kwargs["source"],
            "codex-native-elicitation",
        )
        self.assertNotIn("Do API work.", context.messages[0])

    def test_api_resume_fails_closed_until_separate_native_authorization(self) -> None:
        runtime = Mock()
        runtime.resume.return_value = {"status": "COMPLETED"}
        cancelled = asyncio.run(
            resolve_agent_approval(
                FakeContext(action="cancel"),
                "demo",
                "run-1",
                "approval-1",
                True,
            )
        )
        self.assertEqual(cancelled["status"], "AWAITING_APPROVAL")
        runtime.resume.assert_not_called()

        with patch("codex_bridge.server._agents_sdk_runtime", return_value=runtime):
            approved = asyncio.run(
                resolve_agent_approval(
                    FakeContext(data=NativeApprovalForm(decision="approve")),
                    "demo",
                    "run-1",
                    "approval-1",
                    True,
                )
            )
        self.assertEqual(approved["status"], "COMPLETED")
        runtime.resume.assert_called_once()

    def test_external_action_revalidates_payload_and_records_safe_audit(self) -> None:
        approval = ApprovalRequest(
            approval_id="external-1",
            project_name="demo",
            approval_type="repository_action",
            source_thread_id="",
            source_agent_name="",
            title="Create private repository",
            summary="Create one private repository.",
            payload={"repository": "example/demo", "visibility": "private"},
            status="OPEN",
            created_at="2026-07-19T10:00:00+00:00",
            resolved_at="",
        )
        resolved = ApprovalRequest(
            **{**approval.__dict__, "status": "APPROVED"}
        )
        audit = Mock(return_value={"event_type": "external_approval_decided"})
        with patch("workspace.list_approvals", return_value=[approval]), patch(
            "workspace.approve_request",
            return_value=resolved,
        ) as approve, patch.object(
            WorkflowController,
            "record_native_external_approval_decision",
            audit,
        ):
            result = asyncio.run(
                decide_external_approval(
                    FakeContext(data=NativeApprovalForm(decision="approve")),
                    "demo",
                    approval.approval_id,
                )
            )
        self.assertEqual(result["status"], "APPROVED")
        approve.assert_called_once_with("demo", "external-1")
        audit.assert_called_once()
        audit_kwargs = audit.call_args.kwargs
        self.assertEqual(audit_kwargs["decision"], "approve")
        self.assertNotIn("payload", audit_kwargs)

        changed = ApprovalRequest(
            **{
                **approval.__dict__,
                "summary": "Changed after display.",
            }
        )
        calls = iter([[approval], [changed]])
        with patch("workspace.list_approvals", side_effect=lambda *_: next(calls)), patch(
            "workspace.approve_request",
        ) as stale_approve:
            stale = asyncio.run(
                decide_external_approval(
                    FakeContext(data=NativeApprovalForm(decision="approve")),
                    "demo",
                    approval.approval_id,
                )
            )
        self.assertEqual(stale["status"], "OPEN")
        stale_approve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
