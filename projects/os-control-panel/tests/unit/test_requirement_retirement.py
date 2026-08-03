from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import control_plane.storage as storage
from control_plane import WorkflowController
from pm_contract import PMDecisionEnvelope, PMRequirementChange
from tools.project_registry import ProjectLocation, register_project
from workspace import delete_requirement, load_requirement_document, load_task_document
import app


class RequirementRetirementTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project_root = self.root / "projects" / "demo"
        product = self.project_root / "product"
        product.mkdir(parents=True)
        (self.project_root / "memory.md").write_text("# Memory\n", encoding="utf-8")
        (product / "requirements.md").write_text(
            "# Product Requirements\n\n"
            "## Active Requirements\n\n"
            "Add active requirements here.\n\n"
            "---\n\n"
            "## Backlog (Not yet prioritised)\n\n"
            "### R1 — Historical initiative\n\n"
            "Status: BACKLOG\n"
            "Priority: HIGH\n"
            "Effort: L\n"
            "Description:\n"
            "Delivered useful slices but abandoned the remaining expansion.\n\n"
            "---\n\n"
            "## Rules\n\n"
            "Only one requirement may be IN_PROGRESS.\n",
            encoding="utf-8",
        )
        (product / "tasks.md").write_text(
            "# Tasks\n\n"
            "## Task 1: Delivered slice\n\n"
            "Type: Feature Task\n"
            "Status: DONE\n"
            "Requirement: R1\n\n"
            "Validated delivery.\n\n"
            "## Task 2: Abandoned expansion\n\n"
            "Type: Feature Task\n"
            "Status: BACKLOG\n"
            "Requirement: R1\n\n"
            "No longer planned.\n",
            encoding="utf-8",
        )
        self.environment_patch = patch.dict(
            os.environ,
            {
                "AI_BUILDER_OS_PROJECT_REGISTRY": str(self.root / "registry.json"),
                "AI_BUILDER_OS_RUNTIME_ROOT": str(self.root / "runtime"),
            },
            clear=False,
        )
        self.environment_patch.start()
        register_project(
            ProjectLocation(
                project_id="retirement-test-demo",
                name="demo",
                display_name="Demo",
                mode="attached_repository",
                workspace_path=self.project_root,
                visibility="private",
                ownership="self",
                repository="owner/demo",
            )
        )
        self.repo_patch = patch.object(storage, "REPO_ROOT", self.root)
        self.repo_patch.start()

    def tearDown(self) -> None:
        self.repo_patch.stop()
        self.environment_patch.stop()
        self.temporary.cleanup()

    def test_retirement_preserves_done_tasks_and_retires_open_tasks(self) -> None:
        controller = WorkflowController()
        event = controller.retire_requirement(
            "demo",
            "R1",
            reason="Product Director removed the remaining roadmap scope.",
            actor="product-director-test",
            authorization="R105 revision 1",
            idempotency_key="retire-r1",
        )
        duplicate = controller.retire_requirement(
            "demo",
            "R1",
            reason="Product Director removed the remaining roadmap scope.",
            actor="product-director-test",
            authorization="R105 revision 1",
            idempotency_key="retire-r1",
        )

        requirements = load_requirement_document("demo")
        tasks = {item.number: item for item in load_task_document("demo").tasks}
        retired = requirements.retired_requirements[0]

        self.assertEqual(event["event_id"], duplicate["event_id"])
        self.assertEqual(retired.id, "R1")
        self.assertEqual(retired.status, "RETIRED")
        self.assertIn("- Reason: Product Director removed the remaining roadmap scope.", retired.description)
        self.assertEqual(tasks[1].status, "DONE")
        self.assertEqual(tasks[1].requirements, ("R1",))
        self.assertEqual(tasks[2].status, "RETIRED")
        self.assertEqual(event["preserved_done_tasks"], 1)
        self.assertEqual(event["retired_tasks"], 1)
        self.assertEqual(controller.next_action("demo").next_role, "None")

    def test_destructive_delete_fails_closed_for_completed_delivery_history(self) -> None:
        with self.assertRaisesRegex(ValueError, "completed delivery history"):
            delete_requirement("demo", "R1")

        document = load_requirement_document("demo")
        self.assertEqual(document.backlog_requirements[0].id, "R1")
        self.assertEqual(len(load_task_document("demo").tasks), 2)

    def test_retired_requirement_is_read_only_display_history(self) -> None:
        WorkflowController().retire_requirement(
            "demo",
            "R1",
            reason="The remaining scope is obsolete.",
            actor="product-director-test",
            authorization="R105 revision 1",
        )
        record = load_requirement_document("demo").retired_requirements[0]
        active, done = app.split_requirements_for_display([record])
        metadata = app.requirement_retirement_metadata(record)

        self.assertEqual(active, [])
        self.assertEqual(done, [])
        self.assertEqual(metadata["reason"], "The remaining scope is obsolete.")
        self.assertEqual(metadata["actor"], "product-director-test")
        self.assertEqual(metadata["authorization"], "R105 revision 1")

    def test_pm_retirement_is_read_only_until_exact_proposal_is_approved(self) -> None:
        controller = WorkflowController()
        original_requirements = (self.project_root / "product" / "requirements.md").read_text(
            encoding="utf-8"
        )
        decision = PMDecisionEnvelope(
            project_name="demo",
            mode="requirement_draft",
            status="READY_FOR_APPROVAL",
            next_action="draft_requirement",
            assistant_message="R1 is ready to retire.",
            facts=["R1 is BACKLOG and its remaining scope is no longer planned."],
            requirement_changes=[
                PMRequirementChange(
                    action="retire",
                    requirement_id="R1",
                    title="Historical initiative",
                    status="RETIRED",
                    priority="HIGH",
                    effort="L",
                    description="Delivered useful slices but abandoned the remaining expansion.",
                    retirement_reason="The Product Director removed the remaining roadmap scope.",
                )
            ],
            approval_summary="Retire R1 while preserving completed delivery evidence.",
        )

        proposal = controller.submit_pm_proposal(
            "demo",
            decision,
            actor="pm-test",
            source="unit",
            idempotency_key="retire-r1-proposal",
        )
        fallback = controller.render_pm_proposal_chat_fallback(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
        )

        self.assertEqual(
            (self.project_root / "product" / "requirements.md").read_text(encoding="utf-8"),
            original_requirements,
        )
        self.assertIn("Retirement reason: The Product Director removed", fallback["markdown"])

        controller.approve_pm_proposal(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="product-director-test",
            source="codex-chat",
        )

        requirements = load_requirement_document("demo")
        tasks = {item.number: item for item in load_task_document("demo").tasks}
        events = [
            event
            for event in controller.history("demo")
            if event["event_type"] == "requirement_retired"
        ]
        self.assertEqual([item.id for item in requirements.retired_requirements], ["R1"])
        self.assertEqual(tasks[1].status, "DONE")
        self.assertEqual(tasks[2].status, "RETIRED")
        self.assertEqual(len(events), 1)
        self.assertEqual(
            events[0]["authorization"],
            f"pm-proposal:{proposal['proposal_id']}:{proposal['proposal_revision']}",
        )
        self.assertEqual(events[0]["source"], "codex-chat")

    def test_pm_retirement_cannot_disguise_requirement_edits(self) -> None:
        controller = WorkflowController()
        decision = PMDecisionEnvelope(
            project_name="demo",
            mode="requirement_draft",
            status="READY_FOR_APPROVAL",
            next_action="draft_requirement",
            assistant_message="R1 is ready to retire.",
            requirement_changes=[
                PMRequirementChange(
                    action="retire",
                    requirement_id="R1",
                    title="Rewritten title",
                    status="RETIRED",
                    priority="HIGH",
                    effort="L",
                    description="Delivered useful slices but abandoned the remaining expansion.",
                    retirement_reason="No longer planned.",
                )
            ],
        )

        with self.assertRaisesRegex(ValueError, "preserve the existing requirement content"):
            controller.submit_pm_proposal("demo", decision, actor="pm-test", source="unit")


if __name__ == "__main__":
    unittest.main()
