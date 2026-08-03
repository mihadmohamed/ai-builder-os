from __future__ import annotations

import tempfile
import unittest
import os
from pathlib import Path
from unittest.mock import patch

import control_plane.storage as storage
from control_plane import WorkflowController
from pm_contract import PMDecisionEnvelope, PMRequirementChange, PMTaskChange, PMWorkRequestPayload
from workspace import (
    RequirementDocument,
    RequirementRecord,
    load_requirement_document,
    load_task_document,
    parse_requirement_outcome_profile,
)
from tools.project_registry import ProjectLocation, register_project


class ControlPlaneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        product = self.root / "projects" / "demo" / "product"
        product.mkdir(parents=True)
        for name in ("requirements.md", "tasks.md", "memory.md"):
            (product / name).write_text(f"# {name}\n", encoding="utf-8")
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
                project_id="control-plane-test-demo",
                name="demo",
                display_name="Demo",
                mode="attached_repository",
                workspace_path=self.root / "projects" / "demo",
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

    def write_canonical_project(self, *, requirement_status: str = "IN_PROGRESS", tasks: str = "") -> None:
        product = self.root / "projects" / "demo" / "product"
        (product / "requirements.md").write_text(
            "# Product Requirements\n\n"
            "## Active Requirements\n\n"
            "### R1 — Autonomous delivery\n\n"
            f"Status: {requirement_status}\n"
            "Priority: HIGH\n"
            "Effort: M\n"
            "Description:\n"
            "Problem statement:\nDelivery stops after approval.\n\n"
            "Target user:\nProduct Director.\n\n"
            "Core job-to-be-done:\nApprove once and continue.\n\n"
            "Success criteria:\n- Work continues automatically.\n\n"
            "---\n\n"
            "## Backlog (Not yet prioritised)\n\n"
            "Add backlog requirements here when needed.\n\n"
            "---\n\n"
            "## Rules\n\nOnly one requirement may be IN_PROGRESS.\n",
            encoding="utf-8",
        )
        (product / "tasks.md").write_text("# Tasks\n" + tasks, encoding="utf-8")

    @staticmethod
    def requirement_update_decision(*, tasks: list[PMTaskChange] | None = None) -> PMDecisionEnvelope:
        return PMDecisionEnvelope(
            project_name="demo",
            mode="requirement_draft",
            status="READY_FOR_APPROVAL",
            next_action="draft_requirement",
            assistant_message="Approve autonomous delivery.",
            facts=["R1 is active."],
            assumptions=["Codex chat is the execution host."],
            requirement_changes=[
                PMRequirementChange(
                    action="update",
                    requirement_id="R1",
                    title="Autonomous delivery",
                    status="IN_PROGRESS",
                    priority="HIGH",
                    effort="M",
                    description=(
                        "Problem statement:\nDelivery stops after approval.\n\n"
                        "Target user:\nProduct Director.\n\n"
                        "Core job-to-be-done:\nApprove once and continue.\n\n"
                        "Success criteria:\n- Work continues automatically."
                    ),
                )
            ],
            task_changes=tasks or [],
            approval_summary="Approve R1 once and authorize bounded derived delivery.",
        )

    def test_intent_history_is_idempotent(self) -> None:
        controller = WorkflowController()
        first = controller.record_intent("demo", "Improve approval clarity", actor="test", source="unit", idempotency_key="intent-1")
        second = controller.record_intent("demo", "Improve approval clarity", actor="test", source="unit", idempotency_key="intent-1")

        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(len(controller.history("demo")), 1)

    def test_outcome_profile_is_structured_but_legacy_safe(self) -> None:
        profile = parse_requirement_outcome_profile(
            "Problem statement:\nUsers cannot see progress.\n\n"
            "Target user:\nProduct Directors.\n\n"
            "Core job-to-be-done:\nApprove once.\n\n"
            "Success criteria:\n- Delivery continues.\n\n"
            "Baseline:\nUnknown; collect during rollout.\n\n"
            "Evidence provenance:\nCanonical workflow history."
        )
        legacy = parse_requirement_outcome_profile("A short legacy requirement remains readable.")

        self.assertTrue(profile.is_structured)
        self.assertEqual(profile.success_criteria, ("Delivery continues.",))
        self.assertEqual(profile.baseline, "Unknown; collect during rollout.")
        self.assertFalse(legacy.is_structured)

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

    def test_requirement_approval_queues_implementation_without_task_approval(self) -> None:
        self.write_canonical_project()
        task = PMTaskChange(
            task_number=1,
            title="Implement automatic delivery",
            requirement_ids=["R1"],
            goal="Continue after requirement approval.",
            requirements=["Create one durable implementation request."],
            constraints=["Do not invoke an API model."],
            validation=["The request is READY_FOR_CODEX."],
        )
        controller = WorkflowController()
        proposal = controller.submit_pm_proposal(
            "demo",
            self.requirement_update_decision(tasks=[task]),
            actor="pm",
            source="unit",
            idempotency_key="r1-requirement",
        )

        controller.approve_pm_proposal(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="director",
            source="unit",
        )

        requests = controller.list_codex_work_requests("demo", statuses=("READY_FOR_CODEX",))
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].request_kind, "implementation")
        self.assertEqual(requests[0].payload["task_numbers"], [1])

    def test_one_requirement_approval_can_create_the_sole_active_requirement(self) -> None:
        product = self.root / "projects" / "demo" / "product"
        (product / "requirements.md").write_text(
            "# Product Requirements\n\n## Active Requirements\n\n"
            "Add active requirements here.\n\n---\n\n"
            "## Backlog (Not yet prioritised)\n\nAdd backlog requirements here.\n\n---\n\n"
            "## Rules\n\nOnly one requirement may be IN_PROGRESS.\n",
            encoding="utf-8",
        )
        (product / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        controller = WorkflowController()
        decision = self.requirement_update_decision().model_copy(
            update={
                "requirement_changes": [
                    PMRequirementChange(
                        action="create",
                        requirement_id="R1",
                        title="Autonomous delivery",
                        status="IN_PROGRESS",
                        priority="HIGH",
                        effort="M",
                        description="Approved requirement starts as the sole active item.",
                    )
                ]
            }
        )
        proposal = controller.submit_pm_proposal(
            "demo", decision, actor="pm", source="unit", idempotency_key="new-active"
        )

        controller.approve_pm_proposal(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="director",
            source="unit",
        )

        self.assertEqual(load_requirement_document("demo").active_requirements[0].status, "IN_PROGRESS")
        request = controller.list_codex_work_requests("demo", statuses=("READY_FOR_CODEX",))[0]
        self.assertEqual(request.request_kind, "pm_decision")

    def test_one_requirement_approval_can_activate_an_existing_backlog_requirement(self) -> None:
        self.write_canonical_project(requirement_status="BACKLOG")
        controller = WorkflowController()
        proposal = controller.submit_pm_proposal(
            "demo",
            self.requirement_update_decision(),
            actor="pm",
            source="unit",
            idempotency_key="backlog-active",
        )

        fallback = controller.render_pm_proposal_chat_fallback(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
        )
        self.assertIn("- Action: update", fallback["markdown"])
        self.assertIn("- Status: IN_PROGRESS", fallback["markdown"])

        controller.approve_pm_proposal(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="director",
            source="unit",
        )

        requirement = load_requirement_document("demo").active_requirements[0]
        self.assertEqual(requirement.id, "R1")
        self.assertEqual(requirement.status, "IN_PROGRESS")
        requests = controller.list_codex_work_requests("demo", statuses=("READY_FOR_CODEX",))
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].request_kind, "pm_decision")
        self.assertEqual(requests[0].payload["authorization_proposal_id"], proposal["proposal_id"])

    def test_backlog_activation_still_rejects_a_second_active_requirement(self) -> None:
        product = self.root / "projects" / "demo" / "product"
        (product / "requirements.md").write_text(
            "# Product Requirements\n\n## Active Requirements\n\n"
            "### R2 — Existing active work\n\nStatus: IN_PROGRESS\nPriority: HIGH\nEffort: M\n"
            "Description:\nExisting active scope.\n\n---\n\n"
            "## Backlog (Not yet prioritised)\n\n"
            "### R1 — Autonomous delivery\n\nStatus: BACKLOG\nPriority: HIGH\nEffort: M\n"
            "Description:\nApproved backlog scope.\n\n---\n\n"
            "## Rules\n\nOnly one requirement may be IN_PROGRESS.\n",
            encoding="utf-8",
        )
        controller = WorkflowController()

        with self.assertRaisesRegex(ValueError, "only one requirement IN_PROGRESS"):
            controller.submit_pm_proposal(
                "demo",
                self.requirement_update_decision(),
                actor="pm",
                source="unit",
                idempotency_key="backlog-conflict",
            )

    def test_authorized_derived_task_plan_auto_applies_and_queues_delivery(self) -> None:
        self.write_canonical_project()
        controller = WorkflowController()
        requirement = controller.submit_pm_proposal(
            "demo",
            self.requirement_update_decision(),
            actor="pm",
            source="unit",
            idempotency_key="r1-no-tasks",
        )
        controller.approve_pm_proposal(
            "demo",
            requirement["proposal_id"],
            requirement["proposal_revision"],
            actor="director",
            source="unit",
        )
        planning = controller.list_codex_work_requests("demo", statuses=("READY_FOR_CODEX",))[0]
        self.assertEqual(planning.request_kind, "pm_decision")
        controller.claim_codex_work_request("demo", planning.request_id, actor="codex")
        payload = PMWorkRequestPayload.model_validate(planning.payload)
        decision = PMDecisionEnvelope(
            project_name="demo",
            mode="task_plan",
            status="READY_FOR_APPROVAL",
            next_action="plan_tasks",
            assistant_message="The bounded plan is ready.",
            work_request=payload,
            task_changes=[
                PMTaskChange(
                    task_number=1,
                    title="Deliver the approved requirement",
                    requirement_ids=["R1"],
                    goal="Implement R1.",
                    requirements=["Preserve the approved scope."],
                    constraints=["No API billing."],
                    validation=["Tests pass."],
                )
            ],
            approval_summary="Derived Task 1 from approved R1.",
        )

        applied = controller.submit_pm_proposal(
            "demo",
            decision,
            actor="pm",
            source="unit",
            origin_request_id=planning.request_id,
            idempotency_key="r1-derived-plan",
        )

        self.assertEqual(applied["status"], "AUTO_APPLIED")
        self.assertEqual(load_task_document("demo").tasks[0].number, 1)
        implementation = [
            item
            for item in controller.list_codex_work_requests("demo", statuses=("READY_FOR_CODEX",))
            if item.request_kind == "implementation"
        ]
        self.assertEqual(len(implementation), 1)

    def test_chat_fallback_renders_exact_pending_revision(self) -> None:
        self.write_canonical_project()
        controller = WorkflowController()
        proposal = controller.submit_pm_proposal(
            "demo",
            self.requirement_update_decision(),
            actor="pm",
            source="unit",
            idempotency_key="chat-fallback",
        )

        fallback = controller.render_pm_proposal_chat_fallback(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
        )

        self.assertIn("Autonomous delivery", fallback["markdown"])
        self.assertIn(proposal["proposal_id"], fallback["markdown"])
        self.assertIn("Retained safety gates", fallback["markdown"])
        self.assertEqual(len(fallback["sealed_payload_sha256"]), 64)

    def test_completed_evidence_reconciles_tasks_requirement_and_stale_terminal_tasks(self) -> None:
        self.write_canonical_project(
            tasks=(
                "\n## Task 1: Implement automatic delivery\n\n"
                "Type: Feature Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nImplement it.\n"
            )
        )
        controller = WorkflowController()
        proposal = controller.submit_pm_proposal(
            "demo",
            self.requirement_update_decision(),
            actor="pm",
            source="unit",
            idempotency_key="completion-auth",
        )
        controller.approve_pm_proposal(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="director",
            source="unit",
        )
        packet = controller.claim_implementation("demo", "R1", executor="codex")

        controller.record_implementation_evidence(
            "demo",
            packet.run_id,
            packet.lease_token,
            summary="Implemented and verified all linked tasks.",
            files_changed=["src/controller.py"],
            tests=["unit: passed"],
        )

        requirement = load_requirement_document("demo").active_requirements[0]
        task = load_task_document("demo").tasks[0]
        self.assertEqual(requirement.status, "DONE")
        self.assertEqual(task.status, "DONE")

    def test_partial_blocked_evidence_reconciles_only_typed_tasks_and_surfaces_blocker(self) -> None:
        self.write_canonical_project(
            tasks=(
                "\n## Task 1: Local contract\n\n"
                "Type: Feature Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nImplement it.\n\n"
                "## Task 2: Deterministic manifest\n\n"
                "Type: Feature Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nImplement it.\n\n"
                "## Task 3: Paid validation\n\n"
                "Type: Validation Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nRun it.\n"
            )
        )
        controller = WorkflowController()
        packet = controller.claim_implementation("demo", "R1", executor="codex")
        product = self.root / "projects" / "demo" / "product"

        result = controller.record_implementation_evidence(
            "demo",
            packet.run_id,
            packet.lease_token,
            summary="Local preparation is complete; paid validation remains.",
            files_changed=["src/controller.py"],
            tests=["unit: passed"],
            status="BLOCKED",
            completed_task_numbers=[1, 2],
            blocking_boundary="api_billing",
            blocking_reason="A new exact paid-batch authorization is required.",
            source_requirements_sha256=storage.sha256_file(product / "requirements.md"),
            source_tasks_sha256=storage.sha256_file(product / "tasks.md"),
        )

        tasks = {item.number: item for item in load_task_document("demo").tasks}
        requirement = load_requirement_document("demo").active_requirements[0]
        self.assertEqual(tasks[1].status, "DONE")
        self.assertEqual(tasks[2].status, "DONE")
        self.assertEqual(tasks[3].status, "TODO")
        self.assertEqual(requirement.status, "IN_PROGRESS")
        self.assertEqual(result["evidence"]["completed_task_numbers"], [1, 2])
        self.assertEqual(result["evidence"]["remaining_task_numbers"], [3])

        decision = controller.next_action("demo")
        self.assertEqual(decision.next_role, "Product Director")
        self.assertIn("api billing blocker", decision.next_action)
        self.assertIn("Remaining tasks: 3", decision.why)

    def test_partial_evidence_rejects_unlinked_tasks_and_stale_source_state(self) -> None:
        self.write_canonical_project(
            tasks=(
                "\n## Task 1: Linked task\n\n"
                "Type: Feature Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nImplement it.\n"
            )
        )
        controller = WorkflowController()
        packet = controller.claim_implementation("demo", "R1", executor="codex")
        product = self.root / "projects" / "demo" / "product"
        requirement_hash = storage.sha256_file(product / "requirements.md")
        task_hash = storage.sha256_file(product / "tasks.md")

        with self.assertRaisesRegex(ValueError, "unlinked tasks"):
            controller.record_implementation_evidence(
                "demo",
                packet.run_id,
                packet.lease_token,
                summary="Not valid.",
                files_changed=[],
                tests=[],
                status="BLOCKED",
                completed_task_numbers=[99],
                blocking_boundary="technical",
                blocking_reason="Test.",
                source_requirements_sha256=requirement_hash,
                source_tasks_sha256=task_hash,
            )

        (product / "tasks.md").write_text(
            (product / "tasks.md").read_text(encoding="utf-8") + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "Task source state changed"):
            controller.record_implementation_evidence(
                "demo",
                packet.run_id,
                packet.lease_token,
                summary="Stale.",
                files_changed=[],
                tests=[],
                status="BLOCKED",
                completed_task_numbers=[1],
                blocking_boundary="technical",
                blocking_reason="Test.",
                source_requirements_sha256=requirement_hash,
                source_tasks_sha256=task_hash,
            )

    def test_autonomous_progress_reports_blocked_run_and_requires_new_retry_identity(self) -> None:
        self.write_canonical_project(
            tasks=(
                "\n## Task 1: Paid validation\n\n"
                "Type: Validation Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nRun it.\n"
            )
        )
        controller = WorkflowController()
        proposal = controller.submit_pm_proposal(
            "demo",
            self.requirement_update_decision(),
            actor="pm",
            source="unit",
            idempotency_key="retry-auth",
        )
        controller.approve_pm_proposal(
            "demo",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="director",
            source="unit",
        )
        queued = controller.list_codex_work_requests(
            "demo",
            statuses=("READY_FOR_CODEX",),
        )
        self.assertEqual(len(queued), 1)
        controller.claim_codex_work_request("demo", queued[0].request_id, actor="codex")
        packet = controller.claim_implementation("demo", "R1", executor="codex")
        controller.record_implementation_evidence(
            "demo",
            packet.run_id,
            packet.lease_token,
            summary="Paid validation is waiting.",
            files_changed=[],
            tests=[],
            status="BLOCKED",
            blocking_boundary="api_billing",
            blocking_reason="Approve one exact retry batch.",
        )
        controller.resolve_codex_work_request(
            "demo",
            queued[0].request_id,
            actor="codex",
            status="BLOCKED",
            summary="Approve one exact retry batch.",
            implementation_run_id=packet.run_id,
        )

        blocked = controller.ensure_autonomous_progress("demo", requirement_id="R1")
        self.assertEqual(blocked["state"], "BLOCKED")
        self.assertEqual(blocked["blocking_boundary"], "api_billing")
        with self.assertRaisesRegex(ValueError, "both a new retry identity"):
            controller.ensure_autonomous_progress(
                "demo",
                requirement_id="R1",
                retry_identity="retry-2",
            )
        retried = controller.ensure_autonomous_progress(
            "demo",
            requirement_id="R1",
            retry_identity="retry-2",
            retry_authorization_id="external-approval-2",
        )
        self.assertEqual(retried["state"], "QUEUED_FOR_CODEX")
        self.assertEqual(retried["request"]["payload"]["retry_identity"], "retry-2")
        self.assertEqual(
            retried["request"]["payload"]["retry_authorization_id"],
            "external-approval-2",
        )

    def test_completed_specialist_request_satisfies_structural_gate(self) -> None:
        self.write_canonical_project(
            tasks=(
                "\n## Task 1: Runtime boundary\n\n"
                "Type: Feature Task\nStatus: TODO\nRequirement: R1\n\nGoal:\nImplement it.\n"
            )
        )
        requirements = self.root / "projects" / "demo" / "product" / "requirements.md"
        requirements.write_text(
            requirements.read_text(encoding="utf-8").replace(
                "Delivery stops after approval.",
                "A new background runtime changes the orchestration boundary.",
            ),
            encoding="utf-8",
        )
        controller = WorkflowController()
        request = controller.create_codex_work_request(
            "demo",
            "Review the runtime boundary.",
            requested_by="controller",
            source="unit",
            requested_role="architect",
            requirement_id="R1",
        )
        controller.claim_codex_work_request("demo", request.request_id, actor="codex")
        controller.resolve_codex_work_request(
            "demo",
            request.request_id,
            actor="codex",
            status="COMPLETED",
            summary="Architecture is bounded.",
        )

        decision = controller.next_action("demo")
        self.assertEqual(decision.next_role, "Engineer")
        self.assertIn("already satisfied", decision.why)

    def test_codex_work_request_rejects_unknown_role(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported Codex role"):
            WorkflowController().create_codex_work_request(
                "demo",
                "Do something",
                requested_by="test",
                source="unit",
                requested_role="unbounded_super_agent",
            )

    def test_legacy_codex_work_requests_load_with_structured_defaults(self) -> None:
        legacy = WorkflowController()._codex_work_request_from_dict(
            {
                "request_id": "legacy-1",
                "project_name": "demo",
                "task": "Legacy task",
                "requested_role": "engineer",
                "status": "READY_FOR_CODEX",
                "requested_by": "test",
                "source": "unit",
                "created_at": "2026-07-18T00:00:00+00:00",
            }
        )
        self.assertEqual(legacy.request_kind, "general")
        self.assertEqual(legacy.payload, {})
        self.assertEqual(legacy.result_proposal_id, "")
        self.assertEqual(legacy.result_proposal_revision, 0)

    def test_pre_project_discovery_is_resumable_exact_and_api_dormant(self) -> None:
        controller = WorkflowController()
        session = controller.start_project_discovery(
            {
                "project_name": "client-intake",
                "display_name": "Client Intake",
                "repository_destination": "standalone",
                "visibility": "private",
                "ownership": "client",
                "organisation_or_client_boundary": "Example Client",
            }
        )
        self.assertEqual(session["execution_backend"], "codex_native")
        self.assertEqual(session["foundation"]["project_objectives"]["provenance"], "missing")

        values = {
            "project_objectives": "Reduce enquiry handling time.",
            "target_audience": "Small professional-services teams.",
            "business_goal": "Increase qualified enquiries.",
            "scope": "Include intake and triage; exclude billing.",
            "constraints": "Private, accessible, and mobile-ready.",
            "priority_journeys": "A prospect submits and an operator triages an enquiry.",
            "success_metrics": "Reduce median handling time by 30% in eight weeks.",
        }
        for field, value in values.items():
            session = controller.update_project_discovery_field(
                session["session_id"],
                field,
                value=value,
            )
        resumed = controller.get_project_discovery(session["session_id"])
        self.assertEqual(resumed["foundation"]["success_metrics"]["provenance"], "user_provided")

        prepared = controller.prepare_pre_project_proposal(session["session_id"])
        proposal = prepared["proposal"]
        with self.assertRaisesRegex(ValueError, "seal"):
            controller.approve_pre_project_proposal(
                session["session_id"], exact_seal="wrong", actor="product-director"
            )
        approved = controller.approve_pre_project_proposal(
            session["session_id"],
            exact_seal=proposal["seal"],
            actor="product-director",
        )
        self.assertEqual(approved["status"], "APPROVED")
        self.assertEqual(approved["proposal"]["resolved_by"], "product-director")


if __name__ == "__main__":
    unittest.main()
