from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]


class LearningAgentPreflightTests(unittest.TestCase):
    def test_preflight_fails_without_required_hosted_env(self) -> None:
        env = {"PYTHONPATH": str(REPO_ROOT / "projects" / "learning-agent" / "src")}
        result = subprocess.run(
            [sys.executable, "-m", "preflight"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("OPENAI_API_KEY is missing", result.stdout)
        self.assertIn("LEARNING_AGENT_AUTH_MODE is missing", result.stdout)

    def test_preflight_passes_with_valid_hosted_env(self) -> None:
        env = os.environ.copy()
        env.update(
            {
                "PYTHONPATH": str(REPO_ROOT / "projects" / "learning-agent" / "src"),
                "OPENAI_API_KEY": "sk-test-123",
                "AI_BUILDER_OS_RUNTIME_ROOT": "/data",
                "AI_BUILDER_OS_LEARNING_RELEASE_PROFILE": "external_v2",
                "LEARNING_AGENT_AUTH_MODE": "oidc",
                "LEARNING_AGENT_ALLOWED_EMAILS": "pilot1@example.com,pilot2@example.com",
                "LEARNING_AGENT_PRIVACY_CONTACT": "privacy@yourcompany.com",
                "OIDC_REDIRECT_URI": "https://learning.example.com/oauth2callback",
                "OIDC_COOKIE_SECRET": "abcdefghijklmnopqrstuvwxyz123456",
                "OIDC_CLIENT_ID": "client-id",
                "OIDC_CLIENT_SECRET": "client-secret",
                "OIDC_SERVER_METADATA_URL": "https://accounts.google.com/.well-known/openid-configuration",
            }
        )
        result = subprocess.run(
            [sys.executable, "-m", "preflight"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Hosted pilot preflight passed", result.stdout)
        self.assertNotIn("[FAIL]", result.stdout)


if __name__ == "__main__":
    unittest.main()
