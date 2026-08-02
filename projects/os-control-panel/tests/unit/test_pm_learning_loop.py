from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from control_plane import storage
from control_plane.service import WorkflowController
from control_plane.storage import append_history
from pm_contract import (
    PMDecisionEnvelope,
    PMOutcomeReviewDecision,
    PMRequirementChange,
    PMReviewEvidencePacket,
)
from tools.project_registry import ProjectLocation, register_project
from workspace import load_requirement_document, parse_requirement_outcome_profile
from app import _learning_loop_display_state, _pm_sdk_prompt
from pm_contract import PMWorkRequestPayload


REQUIREMENTS = """# Product Requirements

## Active Requirements

### R1 — Released learning-loop candidate

Status: DONE
Priority: HIGH
Effort: M
Description:
Problem statement:
Users cannot see whether delivery improved the intended outcome.

Target user:
Product Directors.

Core job-to-be-done:
Review released work using attributable evidence.

Desired outcome:
Make one evidence-grounded follow-up decision.

Success and acceptance evidence:
- Weekly activation improves after release.

Measurement window:
7 days after release.

Expected outcome evidence:
- Weekly activation.

Evidence provenance:
Privacy-bounded analytics export.

Evidence confidence:
medium

Constraints:
- Missing evidence is not success.

Out of scope:
- A general analytics platform.

Assumptions:
- A release event is recorded.

Open questions:
- None.

---

## Backlog (Not yet prioritised)

---

## Rules

* Completed requirements are immutable.
"""


class PMLearningLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        product = self.root / "project" / "product"
        product.mkdir(parents=True)
        (product / "requirements.md").write_text(REQUIREMENTS, encoding="utf-8")
        (product / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        (product / "memory.md").write_text("# Memory\n", encoding="utf-8")
        (product / "history.jsonl").write_text("", encoding="utf-8")
        self.environment_patch = patch.dict(
            os.environ,
            {
                "AI_BUILDER_OS_PROJECT_REGISTRY": str(self.root / "registry.json"),
                "AI_BUILDER_OS_RUNTIME_ROOT": str(self.root / "runtime"),
                "OPENAI_API_KEY": "",
            },
            clear=False,
        )
        self.environment_patch.start()
        register_project(
            ProjectLocation(
                project_id="pm-learning-demo",
                name="pm-learning",
                display_name="PM Learning",
                mode="attached_repository",
                workspace_path=self.root / "project",
                visibility="private",
                ownership="self",
                repository="owner/pm-learning",
            )
        )
        self.repo_patch = patch.object(storage, "REPO_ROOT", self.root)
        self.repo_patch.start()
        append_history(
            "pm-learning",
            {
                "event_id": "release-r1",
                "event_type": "release_completed",
                "requirement_id": "R1",
                "status": "RELEASED",
                "summary": "R1 was released.",
                "recorded_at": "2026-07-01T00:00:00+00:00",
            },
        )

    def tearDown(self) -> None:
        self.repo_patch.stop()
        self.environment_patch.stop()
        self.temporary.cleanup()

    def configure_analytics(self, *, requirement_id: str = "R1", occurred_at: str = "2026-07-15T00:00:00+00:00") -> None:
        evidence = self.root / "project" / "product" / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "sources.json").write_text(
            json.dumps(
                {
                    "schema_version": "2026-07-21.pm-evidence-sources.v1",
                    "sources": [
                        {
                            "kind": "analytics",
                            "source_id": "analytics-safe",
                            "owner": "Product",
                            "privacy_boundary": "Aggregated metrics only",
                            "path": "analytics.jsonl",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (evidence / "analytics.jsonl").write_text(
            json.dumps(
                {
                    "id": "activation-1",
                    "title": "Weekly activation",
                    "summary": "Aggregated activation increased.",
                    "requirement_id": requirement_id,
                    "occurred_at": occurred_at,
                    "confidence": "medium",
                    "provenance": "warehouse:activation",
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def test_outcome_profile_and_packet_are_ready_with_current_attributable_evidence(self) -> None:
        self.configure_analytics()
        controller = WorkflowController()
        profile = parse_requirement_outcome_profile(
            load_requirement_document("pm-learning").active_requirements[0].description
        )
        packet = controller.build_pm_review_evidence("pm-learning", "outcome_review", "R1")

        self.assertEqual(profile.expected_outcome_evidence, ("Weekly activation.",))
        self.assertTrue(profile.is_structured)
        self.assertEqual(packet["review_state"], "ready")
        self.assertEqual(packet["review_due_at"], "2026-07-08T00:00:00+00:00")
        self.assertEqual(packet["evidence_confidence"], "medium")
        self.assertIn("analytics-safe", packet["evidence_provenance"])
        self.assertNotIn("analytics", packet["missing_sources"])
        self.assertTrue(
            any(
                item["evidence_type"] == "outcome_signal"
                and item["provenance"] == "warehouse:activation"
                and not item["stale"]
                for item in packet["references"]
            )
        )

    def test_missing_mismatched_and_stale_signals_never_become_success(self) -> None:
        controller = WorkflowController()
        missing = controller.build_pm_review_evidence("pm-learning", "outcome_review", "R1")
        self.assertEqual(missing["review_state"], "insufficient_evidence")
        self.assertIn("analytics", missing["missing_sources"])

        self.configure_analytics(requirement_id="R999")
        mismatched = controller.build_pm_review_evidence("pm-learning", "outcome_review", "R1")
        self.assertEqual(mismatched["review_state"], "insufficient_evidence")
        self.assertIn("analytics", mismatched["missing_sources"])

        self.configure_analytics(occurred_at="2026-06-01T00:00:00+00:00")
        stale = controller.build_pm_review_evidence("pm-learning", "outcome_review", "R1")
        self.assertEqual(stale["review_state"], "insufficient_evidence")
        self.assertIn("Only stale outcome signals are available.", stale["missing_evidence"])
        self.assertTrue(
            any(item["evidence_type"] == "outcome_signal" and item["stale"] for item in stale["references"])
        )

    def test_close_requires_limitation_and_experiment_preserves_follow_up_lineage(self) -> None:
        controller = WorkflowController()
        packet = PMReviewEvidencePacket.model_validate(
            controller.build_pm_review_evidence("pm-learning", "outcome_review", "R1")
        )
        close = PMDecisionEnvelope(
            project_name="pm-learning",
            mode="outcome_review",
            status="READY_FOR_APPROVAL",
            next_action="review_outcome",
            assistant_message="Close the learning review.",
            review_evidence=packet,
            outcome_review=PMOutcomeReviewDecision(
                action="close",
                requirement_id="R1",
                rationale="The Product Director accepts the bounded conclusion.",
            ),
        )
        with self.assertRaisesRegex(ValueError, "explicit limitation"):
            controller.submit_pm_proposal("pm-learning", close, actor="pm", source="unit")

        stop = close.model_copy(
            update={
                "outcome_review": close.outcome_review.model_copy(
                    update={
                        "action": "stop",
                        "evidence_limitation": "No attributable outcome signal is available.",
                    }
                )
            }
        )
        stopped = controller.submit_pm_proposal(
            "pm-learning",
            stop,
            actor="pm",
            source="unit",
            idempotency_key="stop-r1",
        )
        controller.reject_pm_proposal(
            "pm-learning",
            stopped["proposal_id"],
            stopped["proposal_revision"],
            actor="director",
            source="unit",
        )

        follow_up = PMRequirementChange(
            action="create",
            requirement_id="R2",
            title="Validate activation with a bounded experiment",
            status="BACKLOG",
            priority="HIGH",
            effort="S",
            description=(
                "Problem statement:\nActivation evidence is incomplete.\n\n"
                "Target user:\nProduct Directors.\n\n"
                "Core job-to-be-done:\nRun a bounded validation.\n\n"
                "Desired outcome:\nResolve the evidence gap.\n\n"
                "Success and acceptance evidence:\n- A privacy-safe experiment result exists.\n\n"
                "Constraints:\n- Preserve privacy.\n\n"
                "Out of scope:\n- General analytics.\n\n"
                "Assumptions:\n- R1 is the source review.\n\n"
                "Open questions:\n- None."
            ),
        )
        experiment = PMDecisionEnvelope(
            project_name="pm-learning",
            mode="outcome_review",
            status="READY_FOR_APPROVAL",
            next_action="review_outcome",
            assistant_message="Run one bounded experiment.",
            review_evidence=packet,
            outcome_review=PMOutcomeReviewDecision(
                action="experiment",
                requirement_id="R1",
                rationale="Missing outcome evidence warrants a bounded experiment.",
                evidence_limitation="No attributable outcome signal is available.",
                follow_up_requirement_ids=["R2"],
            ),
            requirement_changes=[follow_up],
            approval_summary="Create R2 as the traceable R1 experiment follow-up.",
        )
        proposal = controller.submit_pm_proposal(
            "pm-learning",
            experiment,
            actor="pm",
            source="unit",
        )
        controller.approve_pm_proposal(
            "pm-learning",
            proposal["proposal_id"],
            proposal["proposal_revision"],
            actor="director",
            source="unit",
        )
        history = controller.history("pm-learning")
        event = next(item for item in reversed(history) if item["event_type"] == "pm_proposal_approved")
        self.assertEqual(event["review_target_id"], "R1")
        self.assertEqual(event["follow_up_requirement_ids"], ["R2"])
        self.assertEqual(
            next(item for item in load_requirement_document("pm-learning").backlog_requirements if item.id == "R2").status,
            "BACKLOG",
        )
        refreshed = PMReviewEvidencePacket.model_validate(
            controller.build_pm_review_evidence("pm-learning", "outcome_review", "R1")
        )
        duplicate = experiment.model_copy(
            update={
                "review_evidence": refreshed,
                "outcome_review": experiment.outcome_review.model_copy(
                    update={"follow_up_requirement_ids": ["R3"]}
                ),
                "requirement_changes": [
                    follow_up.model_copy(
                        update={
                            "requirement_id": "R3",
                            "title": "Run another activation experiment",
                        }
                    )
                ],
            }
        )
        with self.assertRaisesRegex(ValueError, "already open"):
            controller.submit_pm_proposal(
                "pm-learning",
                duplicate,
                actor="pm",
                source="unit",
            )

    def test_ui_state_and_sdk_prompt_preserve_approval_and_billing_boundaries(self) -> None:
        self.assertEqual(
            _learning_loop_display_state({"review_state": "ready"}, pending=False),
            "ready",
        )
        self.assertEqual(
            _learning_loop_display_state({"review_state": "ready"}, pending=True),
            "decision_pending",
        )
        prompt = _pm_sdk_prompt(
            PMWorkRequestPayload(
                mode="outcome_review",
                target_requirement_ids=["R1"],
            )
        )
        self.assertIn("missing evidence explicitly", prompt)
        self.assertIn("pauses for human approval", prompt)
