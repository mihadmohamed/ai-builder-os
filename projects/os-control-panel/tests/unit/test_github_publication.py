from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import github_publication  # noqa: E402
import workspace  # noqa: E402


class GitHubPublicationTests(unittest.TestCase):
    def test_publication_policy_allows_canonical_requirement_summary(self) -> None:
        draft = github_publication.draft_issue_from_requirement(
            project_name="os-control-panel",
            requirement_id="R99",
            title="Add delivery status",
            status="IN_PROGRESS",
            priority="HIGH",
            effort="M",
            description="Show delivery status for approved requirements.",
        )

        self.assertTrue(draft.review)
        self.assertTrue(draft.review.allowed)
        self.assertIn("Generated from canonical product truth", draft.body)

    def test_publication_policy_blocks_private_paths_runtime_state_and_secrets(self) -> None:
        review = github_publication.review_publication_payload(
            title="Publish internal note",
            body=(
                "See private/roadmap.md and projects/os-control-panel/data/agent_traces.jsonl. "
                "OPENAI_API_KEY=sk-secret-value"
            ),
        )

        self.assertFalse(review.allowed)
        self.assertEqual(
            {finding.kind for finding in review.findings},
            {"private_path", "runtime_state", "secret"},
        )

    def test_publication_policy_redacts_contact_information_without_blocking(self) -> None:
        review = github_publication.review_publication_payload(
            title="Contact person@example.com",
            body="Call +44 7700 900123 after release.",
        )

        self.assertTrue(review.allowed)
        self.assertIn("<redacted-email>", review.sanitized_title)
        self.assertIn("<redacted-phone>", review.sanitized_body)

    def test_request_github_issue_publication_creates_policy_checked_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            approvals = Path(temp_dir) / "approvals.json"
            approvals.write_text("[]")
            with patch("workspace.APPROVAL_FILE", approvals):
                approval = workspace.request_github_issue_publication("os-control-panel", "R81")
                stored = json.loads(approvals.read_text())

        self.assertEqual(approval.approval_type, "github_publication")
        self.assertEqual(approval.payload["github_target"], "issue")
        self.assertEqual(approval.payload["policy_status"], "PASS")
        self.assertEqual(len(stored), 1)

    def test_policy_language_is_publicized_for_github_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            approvals = Path(temp_dir) / "approvals.json"
            approvals.write_text("[]")
            with patch("workspace.APPROVAL_FILE", approvals):
                approval = workspace.request_github_issue_publication("os-control-panel", "R84")

        self.assertEqual(approval.payload["policy_status"], "PASS")
        self.assertIn("local-only planning detail", approval.payload["github_body"])
        self.assertNotIn("private planning", approval.payload["github_body"].lower())

    def test_publish_issue_uses_github_api(self) -> None:
        with patch.dict(
            "os.environ",
            {"AI_BUILDER_OS_GITHUB_REPO": "owner/repo", "AI_BUILDER_OS_GITHUB_TOKEN": "token"},
            clear=False,
        ):
            with patch("github_publication._github_request") as request:
                request.return_value = {"html_url": "https://github.com/owner/repo/issues/7", "number": 7}
                result = github_publication.publish_github_publication(
                    {
                        "github_target": "issue",
                        "github_title": "R99: Add delivery status",
                        "github_body": "A public issue body.",
                        "policy_status": "PASS",
                    }
                )

        self.assertEqual(result.kind, "issue")
        self.assertEqual(result.reference_id, "7")
        request.assert_called_once()
        self.assertEqual(request.call_args.kwargs["method"], "POST")
        self.assertEqual(request.call_args.kwargs["path"], "/repos/owner/repo/issues")
        self.assertEqual(request.call_args.kwargs["payload"]["title"], "R99: Add delivery status")

    def test_approving_github_publication_publishes_and_records_url(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            approvals = Path(temp_dir) / "approvals.json"
            approvals.write_text("[]")
            result = github_publication.GitHubPublishResult(
                kind="issue",
                url="https://github.com/owner/repo/issues/12",
                reference_id="12",
                detail="Created GitHub issue from approved OS requirement draft.",
            )
            with patch("workspace.APPROVAL_FILE", approvals), patch("workspace.publish_github_publication", return_value=result):
                approval = workspace.request_github_issue_publication("os-control-panel", "R81")
                approved = workspace.approve_request("os-control-panel", approval.approval_id)

        self.assertEqual(approved.status, "APPROVED")
        self.assertEqual(approved.payload["outcome_kind"], "github_publication_published")
        self.assertEqual(approved.payload["publication_state"], "published")
        self.assertEqual(approved.payload["github_published_url"], "https://github.com/owner/repo/issues/12")

    def test_failed_github_publish_leaves_approval_open(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            approvals = Path(temp_dir) / "approvals.json"
            approvals.write_text("[]")
            with patch("workspace.APPROVAL_FILE", approvals):
                approval = workspace.request_github_issue_publication("os-control-panel", "R81")
                with patch(
                    "workspace.publish_github_publication",
                    side_effect=github_publication.GitHubPublishError("GitHub publishing is not configured."),
                ):
                    with self.assertRaises(github_publication.GitHubPublishError):
                        workspace.approve_request("os-control-panel", approval.approval_id)
                stored = json.loads(approvals.read_text())

        self.assertEqual(stored[0]["status"], "OPEN")


if __name__ == "__main__":
    unittest.main()
