from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.create_project import scaffold_project

from project_foundation import (
    FoundationField,
    PreProjectProposal,
    ProjectDiscoverySession,
    ProjectFoundation,
    ProjectIdentity,
    ResearchEvidence,
    ResearchOption,
    derive_initial_requirement,
    foundation_from_markdown,
    load_discovery_session,
    save_discovery_session,
)
from workspace import create_project_from_reviewed_draft


FOUNDATION_MARKDOWN = """Project objectives
Launch a trusted first version that reduces intake time.

Target audience
Small professional-services teams handling client enquiries.

Business goal
Increase qualified enquiries without increasing administration.

Scope
Include enquiry capture and triage; exclude billing and CRM replacement.

Constraints
Private by default, accessible, and usable on mobile.

Priority journeys
A prospective client submits an enquiry and an operator triages it.

Success metrics
Reduce median intake time by 30% within eight weeks while maintaining lead quality.
"""


class ProjectFoundationTests(unittest.TestCase):
    def identity(self) -> ProjectIdentity:
        return ProjectIdentity(project_name="client-intake", display_name="Client Intake")

    def test_complete_foundation_maps_each_concept_once_and_derives_grounded_r1(self) -> None:
        foundation = foundation_from_markdown(self.identity(), FOUNDATION_MARKDOWN)
        title, requirement = derive_initial_requirement(foundation)

        self.assertTrue(foundation.complete)
        self.assertEqual(foundation.missing_fields(), [])
        self.assertIn("Client Intake", title)
        self.assertIn(foundation.foundation_id, requirement)
        self.assertEqual(requirement.count("Small professional-services teams"), 1)
        self.assertNotIn("Project objectives\n", requirement)

    def test_incomplete_foundation_asks_one_stable_next_question_and_blocks_proposal(self) -> None:
        foundation = ProjectFoundation(identity=self.identity()).accept_user_answer(
            "project_objectives", "Validate demand."
        )

        self.assertEqual(foundation.next_gap(), "target_audience")
        self.assertIn("primary audience", foundation.next_question())
        with self.assertRaisesRegex(ValueError, "incomplete"):
            PreProjectProposal(
                foundation=foundation,
                initial_requirement_title="Initial",
                initial_requirement="Draft",
            )

    def test_research_requires_sources_and_explicit_acceptance(self) -> None:
        foundation = ProjectFoundation(identity=self.identity())
        evidence = ResearchEvidence(
            url="https://example.com/research",
            title="Research summary",
            observed_at="2026-08-03",
        )
        option = ResearchOption(
            label="Focus on small teams",
            value="Small professional-services teams",
            tradeoffs=["Narrower initial market"],
            confidence="medium",
            evidence=[evidence],
        )

        self.assertEqual(foundation.target_audience.provenance, "missing")
        accepted = foundation.accept_research_option("target_audience", option)
        self.assertEqual(accepted.target_audience.provenance, "research_accepted")
        self.assertEqual(accepted.target_audience.evidence[0].url, evidence.url)

    def test_research_rejects_unsafe_or_unavailable_evidence(self) -> None:
        with self.assertRaisesRegex(ValueError, "HTTP"):
            ResearchEvidence(
                url="javascript:alert(1)",
                title="Unsafe",
                observed_at="2026-08-03",
            )
        with self.assertRaisesRegex(ValueError, "source evidence"):
            ResearchOption(label="Unsupported", value="An unsupported guess")

    def test_not_applicable_requires_rationale(self) -> None:
        with self.assertRaisesRegex(ValueError, "rationale"):
            FoundationField(provenance="not_applicable")

    def test_assumption_and_not_applicable_states_are_explicit(self) -> None:
        foundation = ProjectFoundation(identity=self.identity())
        assumed = foundation.accept_assumption(
            "project_objectives", "Validate demand before scaling.", "No baseline data exists yet."
        )
        skipped = assumed.mark_not_applicable("constraints", "No additional constraint is known at discovery.")

        self.assertEqual(skipped.project_objectives.provenance, "assumption_accepted")
        self.assertEqual(skipped.constraints.provenance, "not_applicable")
        with self.assertRaisesRegex(ValueError, "rationale"):
            foundation.accept_assumption("project_objectives", "Validate demand.", "")

    def test_preproject_seal_is_stable_for_same_foundation(self) -> None:
        foundation = foundation_from_markdown(self.identity(), FOUNDATION_MARKDOWN)
        title, requirement = derive_initial_requirement(foundation)
        first = PreProjectProposal(
            proposal_id="proposal-1",
            foundation=foundation,
            initial_requirement_title=title,
            initial_requirement=requirement,
            created_at="2026-08-03T00:00:00+00:00",
        )
        second = PreProjectProposal.model_validate(first.model_dump(mode="json"))
        self.assertEqual(first.seal, second.seal)

    def test_exact_approval_rejects_wrong_seal_and_stale_foundation(self) -> None:
        foundation = foundation_from_markdown(self.identity(), FOUNDATION_MARKDOWN)
        session = ProjectDiscoverySession(foundation=foundation).prepare_proposal()
        assert session.proposal is not None

        with self.assertRaisesRegex(ValueError, "seal"):
            session.approve(exact_seal="wrong", actor="product-director")
        changed = session.model_copy(
            update={
                "foundation": foundation.accept_user_answer(
                    "success_metrics", "Reach a 40% reduction within eight weeks."
                )
            }
        )
        with self.assertRaisesRegex(ValueError, "stale"):
            changed.approve(exact_seal=session.proposal.seal, actor="product-director")

        approved = session.approve(exact_seal=session.proposal.seal, actor="product-director")
        self.assertEqual(approved.status, "APPROVED")
        self.assertEqual(approved.proposal.resolved_by, "product-director")

    def test_research_options_are_bounded_distinct_and_require_selection(self) -> None:
        foundation = ProjectFoundation(identity=self.identity())
        session = ProjectDiscoverySession(foundation=foundation)
        evidence = ResearchEvidence(
            url="https://example.com/research",
            title="Research summary",
            observed_at="2026-08-03",
        )
        options = [
            ResearchOption(label="Validate demand", value="Validate demand.", evidence=[evidence]),
            ResearchOption(label="Reduce handling time", value="Reduce handling time.", evidence=[evidence]),
        ]
        offered = session.offer_research("project_objectives", options)

        self.assertEqual(offered.foundation.project_objectives.provenance, "missing")
        selected = offered.select_research("project_objectives", options[1].option_id)
        self.assertEqual(selected.foundation.project_objectives.provenance, "research_accepted")
        with self.assertRaisesRegex(ValueError, "two or three"):
            session.offer_research("project_objectives", options[:1])

    def test_discovery_session_resumes_with_backend_provenance_and_current_gap(self) -> None:
        foundation = ProjectFoundation(identity=self.identity()).accept_user_answer(
            "project_objectives", "Validate demand."
        )
        session = ProjectDiscoverySession(
            execution_backend="codex_native",
            foundation=foundation,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "pre-project.json"
            save_discovery_session(path, session)
            resumed = load_discovery_session(path)

        self.assertIsNotNone(resumed)
        assert resumed is not None
        self.assertEqual(resumed.execution_backend, "codex_native")
        self.assertEqual(resumed.next_gap, "target_audience")
        self.assertEqual(resumed.foundation.project_objectives.provenance, "user_provided")

    def test_scaffold_persists_foundation_and_nonduplicative_r1(self) -> None:
        foundation = foundation_from_markdown(self.identity(), FOUNDATION_MARKDOWN)
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            def scaffold_in_temp(**kwargs: object) -> Path:
                return scaffold_project(**kwargs, workspace_parent=root)  # type: ignore[arg-type]

            with (
                patch("workspace.scaffold_project", side_effect=scaffold_in_temp),
                patch("workspace.save_project_ui_runtime"),
            ):
                destination = create_project_from_reviewed_draft(
                    "client-intake",
                    "Client Intake",
                    "Ignored legacy title",
                    FOUNDATION_MARKDOWN,
                    foundation=foundation,
                )

            self.assertTrue((destination / "product" / "project-foundation.json").exists())
            requirements = (destination / "product" / "requirements.md").read_text(encoding="utf-8")
            self.assertIn(foundation.foundation_id, requirements)
            self.assertNotIn("Project objectives\nLaunch", requirements)


if __name__ == "__main__":
    unittest.main()
