from __future__ import annotations

from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

from control_plane import (
    ACTION_RISKS,
    EXTERNAL_APPROVAL_RISKS,
    ApprovalRisk,
    approval_risk_for_action,
    approval_risk_for_external_type,
    build_action_descriptor,
)


class ApprovalPolicyTests(unittest.TestCase):
    REPO_ROOT = Path(__file__).resolve().parents[4]

    def test_every_registered_action_has_one_stable_risk(self) -> None:
        expected = {
            "list_projects": ApprovalRisk.READ_ONLY,
            "inspect_project": ApprovalRisk.READ_ONLY,
            "get_next_action": ApprovalRisk.READ_ONLY,
            "get_execution_backends": ApprovalRisk.READ_ONLY,
            "get_approval_risk_policy": ApprovalRisk.READ_ONLY,
            "list_pm_proposals": ApprovalRisk.READ_ONLY,
            "describe_pm_proposal_action": ApprovalRisk.READ_ONLY,
            "list_codex_work_requests": ApprovalRisk.READ_ONLY,
            "read_product_history": ApprovalRisk.READ_ONLY,
            "list_agent_approvals": ApprovalRisk.READ_ONLY,
            "list_external_approvals": ApprovalRisk.READ_ONLY,
            "record_product_intent": ApprovalRisk.REVERSIBLE_COORDINATION,
            "submit_pm_proposal": ApprovalRisk.REVERSIBLE_COORDINATION,
            "create_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
            "create_pm_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
            "claim_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
            "resolve_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
            "claim_implementation": ApprovalRisk.REVERSIBLE_COORDINATION,
            "record_implementation_evidence": ApprovalRisk.REVERSIBLE_COORDINATION,
            "approve_pm_proposal": ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
            "reject_pm_proposal": ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
            "decide_pm_proposal": ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
            "decide_external_approval": ApprovalRisk.EXTERNAL_OR_API_BILLED,
            "start_agent_workflow": ApprovalRisk.EXTERNAL_OR_API_BILLED,
            "resolve_agent_approval": ApprovalRisk.EXTERNAL_OR_API_BILLED,
        }
        self.assertEqual(ACTION_RISKS, expected)
        for action, risk in expected.items():
            self.assertEqual(approval_risk_for_action(action), risk)

    def test_external_types_are_classified_separately(self) -> None:
        self.assertEqual(
            EXTERNAL_APPROVAL_RISKS,
            {
                "github_publication": ApprovalRisk.EXTERNAL_OR_API_BILLED,
                "release_delivery": ApprovalRisk.EXTERNAL_OR_API_BILLED,
                "repository_action": ApprovalRisk.EXTERNAL_OR_API_BILLED,
            },
        )
        for approval_type, risk in EXTERNAL_APPROVAL_RISKS.items():
            self.assertEqual(approval_risk_for_external_type(approval_type), risk)

    def test_unknown_actions_and_external_types_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown approval action"):
            approval_risk_for_action("delete_everything")
        with self.assertRaisesRegex(ValueError, "Unknown external approval type"):
            approval_risk_for_external_type("secret_export")
        with patch.dict(
            ACTION_RISKS,
            {"secret_export": ApprovalRisk.DESTRUCTIVE_OR_SECRET_SENSITIVE},
        ):
            with self.assertRaisesRegex(PermissionError, "stronger manual path"):
                build_action_descriptor(
                    project_name="demo",
                    action_name="secret_export",
                    target_type="secret",
                    target_id="redacted",
                    target_revision=0,
                    summary="Export a secret.",
                    source_state={},
                    sealed_payload={},
                )

    def test_malformed_descriptors_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty exact-action fields"):
            build_action_descriptor(
                project_name="demo",
                action_name="approve_pm_proposal",
                target_type="pm_proposal",
                target_id="p1",
                target_revision=1,
                summary="",
                source_state={},
                sealed_payload={},
            )

    def test_seal_binds_revision_source_state_actor_and_idempotency(self) -> None:
        def descriptor(**changes: object) -> str:
            values = {
                "project_name": "demo",
                "action_name": "approve_pm_proposal",
                "target_type": "pm_proposal",
                "target_id": "proposal-1",
                "target_revision": 1,
                "summary": "Approve R1.",
                "source_state": {"requirements_sha256": "aaa"},
                "sealed_payload": {"proposal": "safe fixture"},
                "actor_boundary": "product-director-human",
                "idempotency_identity": "proposal-1:1:approve",
            }
            values.update(changes)
            return build_action_descriptor(**values).sealed_payload_sha256

        baseline = descriptor()
        self.assertNotEqual(baseline, descriptor(target_revision=2))
        self.assertNotEqual(
            baseline,
            descriptor(source_state={"requirements_sha256": "bbb"}),
        )
        self.assertNotEqual(
            baseline,
            descriptor(actor_boundary="automatic-reviewer"),
        )
        self.assertNotEqual(
            baseline,
            descriptor(idempotency_identity="proposal-1:2:approve"),
        )

    def test_human_and_billing_flags_follow_risk(self) -> None:
        canonical = build_action_descriptor(
            project_name="demo",
            action_name="approve_pm_proposal",
            target_type="pm_proposal",
            target_id="p1",
            target_revision=1,
            summary="Approve.",
            source_state={},
            sealed_payload={},
        )
        api = build_action_descriptor(
            project_name="demo",
            action_name="start_agent_workflow",
            target_type="agents_sdk_run",
            target_id="new",
            target_revision=0,
            summary="Start.",
            source_state={},
            sealed_payload={},
        )
        self.assertTrue(canonical.human_approval_required)
        self.assertFalse(canonical.external_side_effect)
        self.assertTrue(api.human_approval_required)
        self.assertTrue(api.external_side_effect)
        self.assertTrue(api.api_billing_possible)

    def test_project_codex_policy_keeps_elicitation_human_reviewed(self) -> None:
        config = tomllib.loads(
            (self.REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8")
        )
        self.assertEqual(config["approval_policy"], "on-request")
        self.assertEqual(config["approvals_reviewer"], "user")
        server = config["mcp_servers"]["ai_builder_os"]
        self.assertEqual(server["default_tools_approval_mode"], "auto")
        self.assertEqual(
            server["tools"]["approve_pm_proposal"]["approval_mode"],
            "prompt",
        )
        self.assertEqual(
            server["tools"]["reject_pm_proposal"]["approval_mode"],
            "prompt",
        )

    def test_reusable_plugin_workflow_contract_stays_synchronized(self) -> None:
        local = self.REPO_ROOT / ".agents" / "skills" / "ai-builder-os-workflow"
        plugin = (
            self.REPO_ROOT
            / "plugins"
            / "ai-builder-os"
            / "skills"
            / "ai-builder-os-workflow"
        )
        for relative in ("SKILL.md", "references/control-plane-contract.md"):
            self.assertEqual(
                (local / relative).read_text(encoding="utf-8"),
                (plugin / relative).read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
