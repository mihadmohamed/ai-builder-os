from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import control_plane.storage as storage
from control_plane import WorkflowController
from workspace import RequirementDocument, RequirementRecord


class ControlPlaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        product = self.root / "projects" / "demo" / "product"
        product.mkdir(parents=True)
        for name in ("requirements.md", "tasks.md", "memory.md"):
            (product / name).write_text(f"# {name}\n", encoding="utf-8")
        self.repo_patch = patch.object(storage, "REPO_ROOT", self.root)
        self.repo_patch.start()

    def tearDown(self) -> None:
        self.repo_patch.stop()
        self.temporary.cleanup()

    def test_intent_history_is_idempotent(self) -> None:
        controller = WorkflowController()
        first = controller.record_intent("demo", "Improve approval clarity", actor="test", source="unit", idempotency_key="intent-1")
        second = controller.record_intent("demo", "Improve approval clarity", actor="test", source="unit", idempotency_key="intent-1")

        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(len(controller.history("demo")), 1)

    def test_claim_and_evidence_require_the_private_lease(self) -> None:
        record = RequirementRecord("R1", "Shared workflow", "NEW", "HIGH", "S", "Implement it")
        document = RequirementDocument("", (record,), (), "")
        controller = WorkflowController()
        with patch("workspace.load_requirement_document", return_value=document):
            packet = controller.claim_implementation("demo", "R1", executor="codex", idempotency_key="claim-1")

        with self.assertRaisesRegex(ValueError, "Invalid run or lease token"):
            controller.record_implementation_evidence(
                "demo", packet.run_id, "wrong", summary="done", files_changed=[], tests=[]
            )

        result = controller.record_implementation_evidence(
            "demo",
            packet.run_id,
            packet.lease_token,
            summary="Implemented shared control plane",
            files_changed=["src/controller.py"],
            tests=["unit: passed"],
        )
        self.assertEqual(result["status"], "COMPLETED")
        self.assertNotIn("lease_token", result)
        self.assertEqual(controller.history("demo")[-1]["event_type"], "implementation_evidence_recorded")

    def test_codex_work_request_has_durable_queue_lifecycle(self) -> None:
        controller = WorkflowController()
        created = controller.create_codex_work_request(
            "demo",
            "Implement the approved workflow",
            requested_by="streamlit-user",
            source="streamlit",
            requested_role="engineer",
            idempotency_key="codex-request-1",
        )
        duplicate = controller.create_codex_work_request(
            "demo",
            "Implement the approved workflow",
            requested_by="streamlit-user",
            source="streamlit",
            requested_role="engineer",
            idempotency_key="codex-request-1",
        )

        self.assertEqual(created.request_id, duplicate.request_id)
        self.assertEqual(created.status, "READY_FOR_CODEX")
        self.assertEqual(
            [item.request_id for item in controller.list_codex_work_requests("demo", statuses=("READY_FOR_CODEX",))],
            [created.request_id],
        )

        claimed = controller.claim_codex_work_request("demo", created.request_id, actor="codex-chat")
        self.assertEqual(claimed.status, "CLAIMED_BY_CODEX")
        resolved = controller.resolve_codex_work_request(
            "demo",
            created.request_id,
            actor="codex-chat",
            status="COMPLETED",
            summary="Implemented and verified",
            implementation_run_id="run-123",
        )
        self.assertEqual(resolved.status, "COMPLETED")
        self.assertEqual(resolved.implementation_run_id, "run-123")
        self.assertEqual(
            [event["event_type"] for event in controller.history("demo")],
            ["codex_work_requested", "codex_work_claimed", "codex_work_resolved"],
        )

    def test_codex_work_request_rejects_unknown_role(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported Codex role"):
            WorkflowController().create_codex_work_request(
                "demo",
                "Do something",
                requested_by="test",
                source="unit",
                requested_role="unbounded_super_agent",
            )


if __name__ == "__main__":
    unittest.main()
