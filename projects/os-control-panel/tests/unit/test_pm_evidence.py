from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from agents_runtime.support import AgentHandBackError, execute_context_tool, pm_mode_tool_names
from control_plane import WorkflowController
import control_plane.storage as storage
from pm_contract import PMDecisionEnvelope, PMModeEvidencePacket, PMRequirementChange
from tools.project_registry import ProjectLocation, register_project


class PMEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        product = self.project / "product"
        product.mkdir(parents=True)
        (product / "requirements.md").write_text(
            "# Product Requirements\n\n## Active Requirements\n\n"
            "### R1 — Evidence\n\nStatus: NEW\nPriority: HIGH\nEffort: S\n"
            "Description:\nUse first-party evidence.\n\n---\n\n"
            "## Backlog (Not yet prioritised)\n\nAdd backlog requirements here.\n\n---\n\n"
            "## Rules\n\nOnly one requirement may be active.\n",
            encoding="utf-8",
        )
        (product / "tasks.md").write_text("# Tasks\n", encoding="utf-8")
        (product / "memory.md").write_text("# Memory\n", encoding="utf-8")
        (product / "history.jsonl").write_text(
            json.dumps({"event_id":"e1","event_type":"intent_recorded","intent":"Use evidence","recorded_at":"2026-07-21T00:00:00+00:00"}) + "\n",
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
        register_project(ProjectLocation(
            project_id="pm-evidence-demo", name="pm-evidence-demo", display_name="PM Evidence Demo",
            mode="attached_repository", workspace_path=self.project, visibility="private", ownership="self", repository="owner/demo",
        ))
        self.repo_patch = patch.object(storage, "REPO_ROOT", self.root)
        self.repo_patch.start()

    def tearDown(self) -> None:
        self.repo_patch.stop()
        self.environment_patch.stop()
        self.temporary.cleanup()

    def test_packet_reports_unconfigured_sources_without_inference(self) -> None:
        packet = PMModeEvidencePacket.model_validate(
            WorkflowController().build_pm_evidence_packet("pm-evidence-demo", "prioritisation", ["R1"])
        )
        self.assertTrue(next(item for item in packet.sources if item.kind == "product_history").available)
        for kind in ("customer_feedback", "analytics", "experiment"):
            source = next(item for item in packet.sources if item.kind == kind)
            self.assertFalse(source.configured)
            self.assertFalse(source.available)
            self.assertIn(kind, packet.missing_sources)

    def test_configured_source_is_bounded_and_filters_private_fields(self) -> None:
        evidence = self.project / "product" / "evidence"
        evidence.mkdir()
        (evidence / "feedback.jsonl").write_text(
            "\n".join(
                json.dumps({
                    "id": f"f{index}", "title": "Observed friction",
                    "summary": "private@example.com reported approval was unclear; token=never",
                    "email": "private@example.com", "secret": "never",
                })
                for index in range(60)
            ) + "\n",
            encoding="utf-8",
        )
        (evidence / "sources.json").write_text(json.dumps({
            "schema_version":"2026-07-21.pm-evidence-sources.v1",
            "sources":[{"kind":"customer_feedback","source_id":"feedback-v1","owner":"Product","privacy_boundary":"Anonymised summaries","path":"feedback.jsonl"}],
        }), encoding="utf-8")

        packet = PMModeEvidencePacket.model_validate(
            WorkflowController().build_pm_evidence_packet("pm-evidence-demo", "discovery", ["R1"])
        )
        source = next(item for item in packet.sources if item.kind == "customer_feedback")
        self.assertTrue(source.available)
        self.assertEqual(source.owner, "Product")
        self.assertEqual(len(source.references), 50)
        self.assertNotIn("email", source.references[0])
        self.assertNotIn("secret", source.references[0])
        self.assertNotIn("private@example.com", source.references[0]["summary"])
        self.assertNotIn("token=never", source.references[0]["summary"])

    def test_configured_path_escape_fails_closed(self) -> None:
        evidence = self.project / "product" / "evidence"
        evidence.mkdir()
        (evidence / "sources.json").write_text(json.dumps({
            "schema_version":"2026-07-21.pm-evidence-sources.v1",
            "sources":[{"kind":"analytics","source_id":"a1","owner":"Product","privacy_boundary":"Aggregate","path":"../../requirements.md"}],
        }), encoding="utf-8")
        packet = PMModeEvidencePacket.model_validate(
            WorkflowController().build_pm_evidence_packet("pm-evidence-demo", "discovery", [])
        )
        source = next(item for item in packet.sources if item.kind == "analytics")
        self.assertFalse(source.available)
        self.assertIn("escapes", source.unavailable_reason)

    def test_role_and_pm_mode_tool_policies_are_enforced(self) -> None:
        self.assertNotIn("web_search", pm_mode_tool_names("task_plan"))
        self.assertIn("web_search", pm_mode_tool_names("discovery"))
        with self.assertRaisesRegex(AgentHandBackError, "task_plan is not allowed"):
            execute_context_tool("PM", "pm-evidence-demo", "web_search", pm_mode="task_plan")
        with self.assertRaisesRegex(AgentHandBackError, "Engineer is not allowed"):
            execute_context_tool("Engineer", "pm-evidence-demo", "read_project_summary")
        self.assertIn(
            "R1",
            execute_context_tool("Engineer", "pm-evidence-demo", "read_requirements"),
        )

    def test_preflight_is_read_only_and_enforces_external_citations(self) -> None:
        controller = WorkflowController()
        decision = PMDecisionEnvelope(
            project_name="pm-evidence-demo", mode="requirement_draft", status="READY_FOR_APPROVAL",
            next_action="draft_requirement", assistant_message="Ready.",
            requirement_changes=[PMRequirementChange(
                action="update", requirement_id="R1", title="Evidence", status="IN_PROGRESS",
                priority="HIGH", effort="S", description="Use first-party evidence.",
            )], approval_summary="Approve R1.",
        )
        before = controller.list_pm_proposals("pm-evidence-demo")
        valid = controller.preflight_pm_proposal("pm-evidence-demo", decision)
        self.assertTrue(valid["valid"])
        self.assertFalse(valid["persisted"])
        self.assertEqual(controller.list_pm_proposals("pm-evidence-demo"), before)

        invalid = decision.model_copy(update={"evidence":["External research: current market claim"]})
        result = controller.preflight_pm_proposal("pm-evidence-demo", invalid)
        self.assertFalse(result["valid"])
        self.assertIn("source URL citation", result["errors"][0])
