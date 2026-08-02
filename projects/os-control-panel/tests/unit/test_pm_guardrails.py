from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import control_plane.storage as storage
from control_plane import WorkflowController
from pm_contract import PMDecisionEnvelope, PMRequirementChange, PMTaskChange
from tools.project_registry import ProjectLocation, register_project


DESCRIPTION = """Problem statement:
Weak proposals can pass review.

Target user:
Product Director.

Core job-to-be-done:
Review an actionable proposal.

Desired outcome:
Unsafe claims fail before approval.

Success and acceptance evidence:
- Blocking findings prevent submission.
- Warnings remain reviewable.

Constraints:
- Use deterministic rules.

Out of scope:
- Subjective strategy scoring.

Assumptions:
- Typed findings are sufficient.

Open questions:
- None."""


class PMGuardrailTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        product = self.root / "project" / "product"
        product.mkdir(parents=True)
        (product / "requirements.md").write_text(
            "# Product Requirements\n\n## Active Requirements\n\n"
            "### R1 — Guardrails\n\nStatus: NEW\nPriority: HIGH\nEffort: M\nDescription:\nExisting.\n\n---\n\n"
            "## Backlog (Not yet prioritised)\n\nAdd backlog requirements here.\n\n---\n\n## Rules\n",
            encoding="utf-8",
        )
        (product / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        (product / "memory.md").write_text("# Memory\n", encoding="utf-8")
        (product / "history.jsonl").write_text("", encoding="utf-8")
        self.env = patch.dict(os.environ, {
            "AI_BUILDER_OS_PROJECT_REGISTRY": str(self.root / "registry.json"),
            "AI_BUILDER_OS_RUNTIME_ROOT": str(self.root / "runtime"),
        }, clear=False)
        self.env.start()
        register_project(ProjectLocation(
            project_id="guardrail-demo", name="guardrail-demo", display_name="Guardrail Demo",
            mode="attached_repository", workspace_path=self.root / "project", visibility="private",
            ownership="self", repository="owner/demo",
        ))
        self.repo = patch.object(storage, "REPO_ROOT", self.root); self.repo.start()

    def tearDown(self) -> None:
        self.repo.stop(); self.env.stop(); self.temporary.cleanup()

    def decision(self, **updates: object) -> PMDecisionEnvelope:
        decision = PMDecisionEnvelope(
            project_name="guardrail-demo", mode="requirement_draft", status="READY_FOR_APPROVAL",
            next_action="draft_requirement", assistant_message="Review.",
            facts=["R1 is NEW"], evidence=["Canonical requirements: R1 status NEW."], assumptions=[],
            requirement_changes=[PMRequirementChange(
                action="update", requirement_id="R1", title="Guardrails", status="IN_PROGRESS",
                priority="HIGH", effort="M", description=DESCRIPTION,
            )], approval_summary="Approve R1.",
        )
        return decision.model_copy(update=updates)

    def test_valid_structured_proposal_has_no_blocking_findings(self) -> None:
        result = WorkflowController().preflight_pm_proposal("guardrail-demo", self.decision())
        self.assertTrue(result["valid"])
        self.assertFalse(any(item["severity"] == "blocking" for item in result["findings"]))

    def test_weak_requirement_and_task_return_actionable_warnings(self) -> None:
        result = WorkflowController().preflight_pm_proposal(
            "guardrail-demo",
            self.decision(
                evidence=[],
                requirement_changes=[PMRequirementChange(
                    action="update", requirement_id="R1", title="Guardrails", status="IN_PROGRESS",
                    priority="HIGH", effort="M", description="Make it better.",
                )],
                task_changes=[PMTaskChange(
                    task_number=1, title="Do it", requirement_ids=["R1"], goal="Fix",
                    requirements=["Improve it."], constraints=["Stay safe."], validation=["It works"],
                )],
            ),
        )
        codes = [item["code"] for item in result["findings"]]
        self.assertTrue(result["valid"])
        self.assertEqual(codes, sorted(codes))
        self.assertIn("facts_without_evidence", codes)
        self.assertIn("missing_requirement_sections", codes)
        self.assertIn("non_testable_acceptance_evidence", codes)
        self.assertIn("vague_task_goal", codes)

    def test_conflicting_fact_and_assumption_blocks_submission(self) -> None:
        decision = self.decision(assumptions=["R1 is NEW"])
        result = WorkflowController().preflight_pm_proposal("guardrail-demo", decision)
        self.assertFalse(result["valid"])
        self.assertIn("fact_assumption_conflict", result["errors"][0])
        with self.assertRaisesRegex(ValueError, "fact_assumption_conflict"):
            WorkflowController().submit_pm_proposal("guardrail-demo", decision, actor="pm", source="unit")

    def test_invalid_state_and_pm_completion_claims_block(self) -> None:
        decision = self.decision(facts=["R1 is DONE", "We have implemented and tested the change."])
        result = WorkflowController().preflight_pm_proposal("guardrail-demo", decision)
        codes = {item["code"] for item in result["findings"] if item["severity"] == "blocking"}
        self.assertEqual(codes, {"invalid_canonical_state_claim", "unsupported_completion_claim"})

    def test_blocking_open_question_requires_needs_input(self) -> None:
        result = WorkflowController().preflight_pm_proposal(
            "guardrail-demo", self.decision(open_questions=["Blocking: who owns this decision?"])
        )
        self.assertFalse(result["valid"])
        self.assertIn("unresolved_blocking_ambiguity", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
