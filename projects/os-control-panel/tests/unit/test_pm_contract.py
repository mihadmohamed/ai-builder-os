from __future__ import annotations

import asyncio
import os
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from agents_runtime.registry import build_agent_registry
from agents_runtime.support import canonical_role_prompt
from control_plane import WorkflowController
from codex_bridge.server import NativeApprovalForm, decide_pm_proposal
import control_plane.storage as storage
from pm_contract import (
    PMDecisionEnvelope,
    PMPrioritisation,
    PMRequirementChange,
    PMTaskChange,
    PMWorkRequestPayload,
)
from tools.project_registry import ProjectLocation, register_project
import app
import workspace


REQUIREMENTS_FIXTURE = """# Product: Demo

# Product Requirements

## Active Requirements

### R1 — Existing requirement

Status: NEW
Priority: HIGH
Effort: S
Description:
Existing product truth.

---

## Backlog (Not yet prioritised)

Add backlog requirements here when needed.

---

## Rules

* Only approved PM proposals change product truth.
"""


class PMContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        product = self.root / "project" / "product"
        product.mkdir(parents=True)
        (product / "requirements.md").write_text(REQUIREMENTS_FIXTURE, encoding="utf-8")
        (product / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        (product / "memory.md").write_text("# Memory\n", encoding="utf-8")
        (product / "history.jsonl").write_text("", encoding="utf-8")
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
                project_id="pm-contract-demo",
                name="pm-demo",
                display_name="PM Demo",
                mode="attached_repository",
                workspace_path=self.root / "project",
                visibility="private",
                ownership="self",
                repository="owner/pm-demo",
            )
        )
        self.repo_patch = patch.object(storage, "REPO_ROOT", self.root)
        self.repo_patch.start()

    def tearDown(self) -> None:
        self.repo_patch.stop()
        self.environment_patch.stop()
        self.temporary.cleanup()

    @staticmethod
    def requirement_decision(*, title: str = "Approved proposal") -> PMDecisionEnvelope:
        return PMDecisionEnvelope(
            project_name="pm-demo",
            mode="requirement_draft",
            status="READY_FOR_APPROVAL",
            next_action="draft_requirement",
            assistant_message="The requirement is ready for approval.",
            facts=["R1 is currently NEW."],
            assumptions=["The first slice stays local-first."],
            requirement_changes=[
                PMRequirementChange(
                    title=title,
                    status="NEW",
                    priority="HIGH",
                    effort="M",
                    description="Create governed proposal and approval behaviour.",
                )
            ],
            approval_summary=f"Create requirement {title}.",
        )

    def test_submit_is_read_only_and_approval_applies_exact_revision(self) -> None:
        controller = WorkflowController()
        original = (self.root / "project" / "product" / "requirements.md").read_text()
        submitted = controller.submit_pm_proposal(
            "pm-demo",
            self.requirement_decision(),
            actor="pm-test",
            source="unit",
            idempotency_key="proposal-1",
        )

        self.assertEqual(submitted["status"], "PENDING_APPROVAL")
        self.assertEqual((self.root / "project" / "product" / "requirements.md").read_text(), original)
        materialized = PMDecisionEnvelope.model_validate(submitted["proposal"])
        self.assertEqual(materialized.requirement_changes[0].requirement_id, "R2")

        approved = controller.approve_pm_proposal(
            "pm-demo",
            submitted["proposal_id"],
            submitted["proposal_revision"],
            actor="product-director",
            source="codex-chat",
        )
        duplicate = controller.approve_pm_proposal(
            "pm-demo",
            submitted["proposal_id"],
            submitted["proposal_revision"],
            actor="product-director",
            source="codex-chat",
        )

        self.assertEqual(approved["status"], "APPROVED")
        self.assertEqual(duplicate["status"], "APPROVED")
        records = workspace.load_requirement_document("pm-demo")
        self.assertEqual([item.id for item in records.active_requirements], ["R1", "R2"])
        approvals = [event for event in controller.history("pm-demo") if event["event_type"] == "pm_proposal_approved"]
        self.assertEqual(len(approvals), 1)
        self.assertEqual(approvals[0]["actor"], "product-director")
        self.assertEqual(approvals[0]["source"], "codex-chat")

    def test_native_codex_approval_accept_reject_cancel_failure_retry_and_malformed(self) -> None:
        class Context:
            def __init__(self, *, action: str = "accept", data: object = None, error: Exception | None = None):
                self.action = action
                self.data = data
                self.error = error

            async def elicit(self, **_: object) -> object:
                if self.error is not None:
                    raise self.error
                return SimpleNamespace(action=self.action, data=self.data)

        controller = WorkflowController()
        approved_proposal = controller.submit_pm_proposal(
            "pm-demo",
            self.requirement_decision(title="Native approved"),
            actor="pm",
            source="unit",
        )
        approve_context = Context(data=NativeApprovalForm(decision="approve"))
        approved = asyncio.run(
            decide_pm_proposal(
                approve_context,
                "pm-demo",
                approved_proposal["proposal_id"],
                approved_proposal["proposal_revision"],
            )
        )
        duplicate = asyncio.run(
            decide_pm_proposal(
                approve_context,
                "pm-demo",
                approved_proposal["proposal_id"],
                approved_proposal["proposal_revision"],
            )
        )
        self.assertEqual(approved["status"], "APPROVED")
        self.assertEqual(duplicate["status"], "APPROVED")

        rejected_proposal = controller.submit_pm_proposal(
            "pm-demo",
            self.requirement_decision(title="Native rejected"),
            actor="pm",
            source="unit",
        )
        rejected = asyncio.run(
            decide_pm_proposal(
                Context(data={"decision": "reject", "rejection_reason": "Not now."}),
                "pm-demo",
                rejected_proposal["proposal_id"],
                rejected_proposal["proposal_revision"],
            )
        )
        self.assertEqual(rejected["status"], "REJECTED")

        for title, context, expected_status in (
            ("Native cancelled", Context(action="cancel"), "PENDING_APPROVAL"),
            ("Native unsupported", Context(error=RuntimeError("unsupported")), "FALLBACK_REQUIRED"),
            (
                "Native malformed",
                Context(data={"decision": "approve", "unexpected": "private"}),
                "PENDING_APPROVAL",
            ),
        ):
            proposal = controller.submit_pm_proposal(
                "pm-demo",
                self.requirement_decision(title=title),
                actor="pm",
                source="unit",
            )
            result = asyncio.run(
                decide_pm_proposal(
                    context,
                    "pm-demo",
                    proposal["proposal_id"],
                    proposal["proposal_revision"],
                )
            )
            self.assertEqual(result["status"], expected_status)
            pending_ids = {
                item["proposal_id"]
                for item in controller.list_pm_proposals(
                    "pm-demo",
                    statuses=("PENDING_APPROVAL",),
                )
            }
            self.assertIn(proposal["proposal_id"], pending_ids)

    def test_native_codex_approval_revalidates_stale_source_state(self) -> None:
        controller = WorkflowController()
        proposal = controller.submit_pm_proposal(
            "pm-demo",
            self.requirement_decision(title="Stale native approval"),
            actor="pm",
            source="unit",
        )
        workspace.update_requirement(
            "pm-demo",
            workspace.RequirementRecord(
                id="R1",
                title="Existing requirement",
                status="NEW",
                priority="HIGH",
                effort="S",
                description="Changed after the prompt descriptor was prepared.",
            ),
        )

        class Context:
            async def elicit(self, **_: object) -> object:
                return SimpleNamespace(
                    action="accept",
                    data=NativeApprovalForm(decision="approve"),
                )

        result = asyncio.run(
            decide_pm_proposal(
                Context(),
                "pm-demo",
                proposal["proposal_id"],
                proposal["proposal_revision"],
            )
        )
        self.assertEqual(result["status"], "STALE_OR_INVALID")
        pending = controller.list_pm_proposals(
            "pm-demo",
            statuses=("PENDING_APPROVAL",),
        )
        self.assertIn(proposal["proposal_id"], {item["proposal_id"] for item in pending})

    def test_task_plan_is_typed_and_links_only_known_requirements(self) -> None:
        controller = WorkflowController()
        workspace.update_requirement(
            "pm-demo",
            workspace.RequirementRecord(
                id="R1",
                title="Existing requirement",
                status="IN_PROGRESS",
                priority="HIGH",
                effort="S",
                description="Existing product truth.",
            ),
        )
        decision = PMDecisionEnvelope(
            project_name="pm-demo",
            mode="task_plan",
            status="READY_FOR_APPROVAL",
            next_action="plan_tasks",
            assistant_message="The task plan is ready.",
            task_changes=[
                PMTaskChange(
                    title="Validate the PM boundary",
                    task_type="Validation Task",
                    requirement_ids=["R1"],
                    goal="Prove that PM remains proposal-only.",
                    requirements=["Exercise submit, approve, reject, and stale-state paths."],
                    constraints=["Do not invoke an API-backed model."],
                    validation=["Confirm canonical files change only after approval."],
                )
            ],
        )
        submitted = controller.submit_pm_proposal("pm-demo", decision, actor="pm", source="unit")
        materialized = PMDecisionEnvelope.model_validate(submitted["proposal"])
        self.assertEqual(materialized.task_changes[0].task_number, 1)
        controller.approve_pm_proposal(
            "pm-demo",
            submitted["proposal_id"],
            submitted["proposal_revision"],
            actor="director",
            source="streamlit",
        )
        tasks = workspace.load_task_document("pm-demo")
        self.assertEqual(tasks.tasks[0].requirements, ("R1",))
        self.assertEqual(tasks.tasks[0].task_type, "Validation Task")

    def test_typed_pm_work_request_links_queue_proposal_and_result(self) -> None:
        controller = WorkflowController()
        workspace.append_requirement(
            "pm-demo",
            "Second candidate",
            "A second NEW requirement for prioritisation.",
            status="NEW",
        )
        payload = PMWorkRequestPayload(
            mode="prioritisation",
            target_requirement_ids=["R1", "R2"],
            operator_context="Prefer the smallest high-value next slice.",
        )
        request = controller.create_pm_codex_work_request(
            "pm-demo",
            payload,
            requested_by="director",
            source="streamlit",
            idempotency_key="typed-pm-request",
        )
        controller.claim_codex_work_request("pm-demo", request.request_id, actor="codex")
        decision = PMDecisionEnvelope(
            project_name="pm-demo",
            mode="prioritisation",
            status="READY_FOR_APPROVAL",
            next_action="prioritise_requirements",
            assistant_message="R1 should run next.",
            prioritisation=PMPrioritisation(
                selected_requirement_id="R1",
                deferred_requirement_ids=["R2"],
                rationale="R1 has the strongest value-to-effort ratio.",
                strategy_alignment="continues",
                evidence_basis="Both candidates are NEW; R1 is smaller and higher priority.",
            ),
            requirement_changes=[
                PMRequirementChange(
                    action="update",
                    requirement_id="R1",
                    title="Existing requirement",
                    status="IN_PROGRESS",
                    priority="HIGH",
                    effort="S",
                    description="Existing product truth.",
                )
            ],
            approval_summary="Activate R1 and defer R2.",
        )
        proposal = controller.submit_pm_proposal(
            "pm-demo",
            decision,
            actor="pm",
            source="codex-mcp",
            origin_request_id=request.request_id,
        )
        resolved = controller.resolve_codex_work_request(
            "pm-demo",
            request.request_id,
            actor="codex",
            status="COMPLETED",
            summary="Submitted a typed PM proposal.",
            result_proposal_id=proposal["proposal_id"],
            result_proposal_revision=proposal["proposal_revision"],
        )

        self.assertEqual(resolved.request_kind, "pm_decision")
        self.assertEqual(resolved.payload["mode"], "prioritisation")
        self.assertEqual(resolved.result_proposal_id, proposal["proposal_id"])
        self.assertEqual(proposal["origin_request_id"], request.request_id)
        self.assertEqual(
            PMDecisionEnvelope.model_validate(proposal["proposal"]).work_request,
            payload,
        )

    def test_operational_pm_requests_enforce_eligibility_and_continuation(self) -> None:
        controller = WorkflowController()
        workspace.append_requirement(
            "pm-demo",
            "Second candidate",
            "A second NEW requirement for prioritisation.",
            status="NEW",
        )
        payload = PMWorkRequestPayload(
            mode="prioritisation",
            target_requirement_ids=["R1", "R2"],
        )
        request = controller.create_pm_codex_work_request(
            "pm-demo",
            payload,
            requested_by="director",
            source="streamlit",
        )
        needs_input = PMDecisionEnvelope(
            project_name="pm-demo",
            mode="prioritisation",
            status="NEEDS_INPUT",
            next_action="ask_question",
            assistant_message="Which outcome is most urgent?",
            open_questions=["Which outcome is most urgent?"],
        )
        proposal = controller.submit_pm_proposal(
            "pm-demo",
            needs_input,
            actor="pm",
            source="codex",
            origin_request_id=request.request_id,
        )
        controller.resolve_codex_work_request(
            "pm-demo",
            request.request_id,
            actor="codex",
            status="COMPLETED",
            summary="PM needs product input.",
            result_proposal_id=proposal["proposal_id"],
            result_proposal_revision=proposal["proposal_revision"],
        )
        continuation = controller.create_pm_codex_work_request(
            "pm-demo",
            payload.model_copy(
                update={
                    "operator_context": "Reduce approval friction first.",
                    "parent_proposal_id": proposal["proposal_id"],
                    "parent_proposal_revision": proposal["proposal_revision"],
                }
            ),
            requested_by="director",
            source="streamlit",
        )
        self.assertEqual(
            continuation.payload["parent_proposal_id"],
            proposal["proposal_id"],
        )

        workspace.update_requirement(
            "pm-demo",
            workspace.RequirementRecord(
                id="R1",
                title="Existing requirement",
                status="IN_PROGRESS",
                priority="HIGH",
                effort="S",
                description="Existing product truth.",
            ),
        )
        with self.assertRaisesRegex(ValueError, "while R1 is IN_PROGRESS"):
            controller.create_pm_codex_work_request(
                "pm-demo",
                payload,
                requested_by="director",
                source="streamlit",
            )

    def test_operational_sdk_proposals_require_the_typed_work_request(self) -> None:
        controller = WorkflowController()
        decision = PMDecisionEnvelope(
            project_name="pm-demo",
            mode="task_plan",
            status="NEEDS_INPUT",
            next_action="ask_question",
            assistant_message="What is the release constraint?",
        )
        with self.assertRaisesRegex(ValueError, "must echo their typed work request"):
            controller.submit_pm_proposal(
                "pm-demo",
                decision,
                actor="pm",
                source="streamlit",
                origin_sdk_run_id="sdk-run-1",
            )

    def test_streamlit_operational_adapter_preserves_backend_and_exact_sdk_approval(self) -> None:
        payload = PMWorkRequestPayload(
            mode="task_plan",
            target_requirement_ids=["R1"],
            operator_context="Prefer one validation task before feature work.",
        )
        prompt = app._pm_sdk_prompt(payload)
        self.assertIn(payload.model_dump_json(indent=2), prompt)
        self.assertIn("Echo the complete typed request", prompt)
        approvals = [
            {
                "project_name": "pm-demo",
                "run_id": "run-1",
                "approval_id": "run-1:0",
                "tool_name": "apply_pm_proposal",
                "arguments": json.dumps(
                    {"proposal_id": "proposal-1", "proposal_revision": 2}
                ),
            }
        ]
        matched = app._sdk_pm_approval("pm-demo", "proposal-1", 2, approvals)
        self.assertEqual(matched["run_id"], "run-1")
        self.assertIsNone(app._sdk_pm_approval("pm-demo", "proposal-1", 1, approvals))

    def test_only_operational_sdk_pm_approvals_move_to_the_pm_inbox(self) -> None:
        operational = PMDecisionEnvelope(
            project_name="pm-demo",
            mode="task_plan",
            status="NEEDS_INPUT",
            next_action="ask_question",
            assistant_message="Which validation constraint matters most?",
            work_request=PMWorkRequestPayload(
                mode="task_plan",
                target_requirement_ids=["R1"],
            ),
        )
        discovery = self.requirement_decision(title="Draft requirement")
        controller = WorkflowController()
        with patch.object(
            app,
            "WorkflowController",
            return_value=controller,
        ), patch.object(
            controller,
            "list_pm_proposals",
            return_value=[
                {
                    "proposal_id": "operational",
                    "proposal_revision": 1,
                    "proposal": operational.model_dump(mode="json"),
                },
                {
                    "proposal_id": "discovery",
                    "proposal_revision": 1,
                    "proposal": discovery.model_dump(mode="json"),
                },
            ],
        ):
            self.assertTrue(
                app._is_operational_sdk_pm_approval(
                    {
                        "project_name": "pm-demo",
                        "tool_name": "apply_pm_proposal",
                        "arguments": {
                            "proposal_id": "operational",
                            "proposal_revision": 1,
                        },
                    }
                )
            )
            self.assertFalse(
                app._is_operational_sdk_pm_approval(
                    {
                        "project_name": "pm-demo",
                        "tool_name": "apply_pm_proposal",
                        "arguments": {
                            "proposal_id": "discovery",
                            "proposal_revision": 1,
                        },
                    }
                )
            )

    def test_failed_operational_codex_request_does_not_require_a_proposal_result(self) -> None:
        controller = WorkflowController()
        workspace.update_requirement(
            "pm-demo",
            workspace.RequirementRecord(
                id="R1",
                title="Existing requirement",
                status="IN_PROGRESS",
                priority="HIGH",
                effort="S",
                description="Existing product truth.",
            ),
        )
        request = controller.create_pm_codex_work_request(
            "pm-demo",
            PMWorkRequestPayload(mode="task_plan", target_requirement_ids=["R1"]),
            requested_by="director",
            source="streamlit",
        )
        controller.claim_codex_work_request("pm-demo", request.request_id, actor="codex")
        resolved = controller.resolve_codex_work_request(
            "pm-demo",
            request.request_id,
            actor="codex",
            status="FAILED",
            summary="The Codex chat could not complete the PM decision.",
        )
        self.assertEqual(resolved.status, "FAILED")
        self.assertFalse(resolved.result_proposal_id)

    def test_stale_and_rejected_proposals_do_not_change_product_truth(self) -> None:
        controller = WorkflowController()
        stale = controller.submit_pm_proposal(
            "pm-demo",
            self.requirement_decision(title="Stale proposal"),
            actor="pm",
            source="unit",
        )
        tasks_path = self.root / "project" / "product" / "tasks.md"
        tasks_path.write_text("# Tasks\n\nExternal change.\n", encoding="utf-8")
        before = (self.root / "project" / "product" / "requirements.md").read_text()
        with self.assertRaisesRegex(ValueError, "source state is stale"):
            controller.approve_pm_proposal(
                "pm-demo",
                stale["proposal_id"],
                stale["proposal_revision"],
                actor="director",
                source="unit",
            )
        self.assertEqual((self.root / "project" / "product" / "requirements.md").read_text(), before)

        refreshed = controller.submit_pm_proposal(
            "pm-demo",
            self.requirement_decision(title="Rejected proposal"),
            actor="pm",
            source="unit",
        )
        rejected = controller.reject_pm_proposal(
            "pm-demo",
            refreshed["proposal_id"],
            refreshed["proposal_revision"],
            actor="director",
            source="codex-chat",
            reason="Not in this release.",
        )
        self.assertEqual(rejected["status"], "REJECTED")
        self.assertNotIn("Rejected proposal", (self.root / "project" / "product" / "requirements.md").read_text())

    def test_application_failure_rolls_back_the_entire_change_bundle(self) -> None:
        controller = WorkflowController()
        decision = self.requirement_decision(title="Atomic proposal")
        decision = decision.model_copy(
            update={
                "task_changes": [
                    PMTaskChange(
                        title="Atomic task",
                        requirement_ids=["R2"],
                        goal="Apply the complete PM bundle.",
                        requirements=["Create requirement and task together."],
                        validation=["Confirm no partial state remains on failure."],
                    )
                ]
            }
        )
        submitted = controller.submit_pm_proposal("pm-demo", decision, actor="pm", source="unit")
        requirements_path = self.root / "project" / "product" / "requirements.md"
        tasks_path = self.root / "project" / "product" / "tasks.md"
        original_requirements = requirements_path.read_text()
        original_tasks = tasks_path.read_text()
        with patch("workspace.save_task_document", side_effect=OSError("simulated write failure")):
            with self.assertRaisesRegex(OSError, "simulated write failure"):
                controller.approve_pm_proposal(
                    "pm-demo",
                    submitted["proposal_id"],
                    submitted["proposal_revision"],
                    actor="director",
                    source="unit",
                )
        self.assertEqual(requirements_path.read_text(), original_requirements)
        self.assertEqual(tasks_path.read_text(), original_tasks)
        pending = controller.list_pm_proposals("pm-demo", statuses=("PENDING_APPROVAL",))
        self.assertEqual(len(pending), 1)

    def test_needs_input_and_duplicate_invariants_are_enforced(self) -> None:
        controller = WorkflowController()
        invalid = self.requirement_decision().model_copy(
            update={
                "status": "NEEDS_INPUT",
                "next_action": "ask_question",
            }
        )
        with self.assertRaisesRegex(ValueError, "cannot contain canonical changes"):
            controller.submit_pm_proposal("pm-demo", invalid, actor="pm", source="unit")

        duplicate = self.requirement_decision(title="Existing requirement")
        with self.assertRaisesRegex(ValueError, "Duplicate PM requirement title"):
            controller.submit_pm_proposal("pm-demo", duplicate, actor="pm", source="unit")

    def test_streamlit_adapter_uses_the_shared_pm_decision(self) -> None:
        question = PMDecisionEnvelope(
            mode="discovery",
            status="NEEDS_INPUT",
            next_action="ask_question",
            assistant_message="Who is the primary user?",
        )
        question_turn = workspace._live_pm_turn_from_decision(question)
        self.assertEqual(question_turn.next_action, "ask_question")

        draft = self.requirement_decision()
        draft_turn = workspace._live_pm_turn_from_decision(draft)
        self.assertEqual(draft_turn.next_action, "draft_requirements")
        self.assertEqual(draft_turn.draft_title, "Approved proposal")

    def test_canonical_contract_is_complete_and_shared_by_sdk_and_codex(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        role_text = (repo_root / "agent" / "roles" / "pm.md").read_text(encoding="utf-8")
        prompt = canonical_role_prompt("PM", "Return the typed decision.")
        codex_definition = (repo_root / ".codex" / "agents" / "pm.toml").read_text(encoding="utf-8")
        registry = build_agent_registry()
        pm = registry["pm"]
        tool_names = {tool.name for tool in pm.tools}

        self.assertIn(role_text.strip(), prompt)
        self.assertIn("## Final Validation", prompt)
        self.assertIn("agent/roles/pm.md", codex_definition)
        self.assertIs(pm.output_type, PMDecisionEnvelope)
        self.assertIn("submit_pm_decision", tool_names)
        approval_tool = next(tool for tool in pm.tools if tool.name == "apply_pm_proposal")
        self.assertTrue(approval_tool.needs_approval)
        self.assertNotIn("download_site_images", tool_names)
        self.assertNotIn("classify_downloaded_site_assets", tool_names)
        for consultation in (
            "architecture_consult",
            "engineering_consult",
            "qa_consult",
            "experience_consult",
            "ui_consult",
        ):
            self.assertIn(consultation, tool_names)


if __name__ == "__main__":
    unittest.main()
