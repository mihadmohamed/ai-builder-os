from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import agent_runtime  # noqa: E402
import tenancy  # noqa: E402
import workspace  # noqa: E402


class HostedLearningTests(unittest.TestCase):
    def test_standalone_navigation_renders_agent_owned_learning_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    workspace.RUNTIME_ROOT_ENV: temp_dir,
                    "LEARNING_AGENT_AUTH_MODE": "local",
                    "LEARNING_AGENT_LOCAL_USER": "navigation-test@example.com",
                },
            ):
                app = AppTest.from_file(
                    str(REPO_ROOT / "projects" / "learning-agent" / "src" / "app.py"),
                    default_timeout=30,
                ).run()

                app.button_group[0].set_value("Learning plan").run()

                self.assertEqual(app.session_state["os-learning-section"], "Learning plan")
                self.assertTrue(app.session_state["os-learning-selected-concept"])
                self.assertTrue(any(button.label in {"Start current step in Learn next", "Resume current step in Learn next"} for button in app.button))
                self.assertTrue(any("**Agent workflow systems**" in text.value for text in app.markdown))
                self.assertTrue(any("**Evals and reliability**" in text.value for text in app.markdown))
                self.assertTrue(any("Current step:" in text.value for text in app.markdown))
                self.assertTrue(any("**How it works**" in text.value for text in app.markdown))
                self.assertTrue(any("**Pilot boundary**" in text.value for text in app.markdown))

    def test_user_id_normalization_is_stable_and_non_revealing(self) -> None:
        first = tenancy.normalize_user_id("Learner@example.com")
        second = tenancy.normalize_user_id("learner@example.com")

        self.assertEqual(first, second)
        self.assertNotEqual(first, tenancy.normalize_user_id("other@example.com"))
        self.assertNotIn("@", first)

    def test_learning_profile_is_isolated_by_active_user(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {workspace.RUNTIME_ROOT_ENV: temp_dir}):
                first_token = tenancy.set_active_user("first@example.com")
                try:
                    workspace.save_learning_profile(
                        product_background="First learner",
                        technical_comfort="First comfort",
                        os_understanding_level="New to AI Builder OS",
                        current_trajectory="First trajectory",
                        credibility_goal="First goal",
                        preferred_learning_style="First style",
                        current_learning_posture="First posture",
                    )
                finally:
                    tenancy.reset_active_user(first_token)

                second_token = tenancy.set_active_user("second@example.com")
                try:
                    second_profile = workspace.load_learning_profile()
                    workspace.save_learning_profile(
                        product_background="Second learner",
                        technical_comfort="Second comfort",
                        os_understanding_level="Know the basics of AI Builder OS",
                        current_trajectory="Second trajectory",
                        credibility_goal="Second goal",
                        preferred_learning_style="Second style",
                        current_learning_posture="Second posture",
                    )
                finally:
                    tenancy.reset_active_user(second_token)

                first_token = tenancy.set_active_user("first@example.com")
                try:
                    first_profile = workspace.load_learning_profile()
                finally:
                    tenancy.reset_active_user(first_token)

        self.assertNotEqual(second_profile["product_background"], "First learner")
        self.assertEqual(first_profile["product_background"], "First learner")

    def test_agent_traces_are_isolated_by_active_user(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {agent_runtime.RUNTIME_ROOT_ENV: temp_dir}):
                first_token = tenancy.set_active_user("first@example.com")
                try:
                    first_path = agent_runtime.append_agent_trace(
                        "os-control-panel",
                        {"trace_id": "first", "event": "run_started"},
                    )
                finally:
                    tenancy.reset_active_user(first_token)

                second_token = tenancy.set_active_user("second@example.com")
                try:
                    second_traces = agent_runtime.load_agent_traces("os-control-panel")
                    second_path = agent_runtime.append_agent_trace(
                        "os-control-panel",
                        {"trace_id": "second", "event": "run_started"},
                    )
                finally:
                    tenancy.reset_active_user(second_token)

        self.assertEqual(second_traces, [])
        self.assertNotEqual(first_path, second_path)
        self.assertIn("users", first_path.parts)

    def test_hosted_learning_package_has_required_deployment_files(self) -> None:
        project = REPO_ROOT / "projects" / "learning-agent"
        required = (
            "src/app.py",
            "Dockerfile",
            "start.sh",
            "requirements.txt",
            "railway.toml",
            "render.yaml",
            "deployment-phases.md",
            ".streamlit/config.toml",
            ".streamlit/secrets.example.toml",
        )

        self.assertTrue(all((project / relative).exists() for relative in required))
        source = (project / "src" / "app.py").read_text(encoding="utf-8")
        self.assertIn("render_learning_tab", source)
        self.assertNotIn("render_operations_tab", source)
        self.assertIn("LEARNING_AGENT_ALLOWED_EMAILS", source)

    def test_signed_out_oidc_state_explains_pilot_shell(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    workspace.RUNTIME_ROOT_ENV: temp_dir,
                    "LEARNING_AGENT_AUTH_MODE": "oidc",
                    "LEARNING_AGENT_PRIVACY_CONTACT": "privacy@example.com",
                },
            ):
                app = AppTest.from_file(
                    str(REPO_ROOT / "projects" / "learning-agent" / "src" / "app.py"),
                    default_timeout=30,
                ).run()

        self.assertTrue(any("Invite-only pilot" in text.value for text in app.caption))
        self.assertTrue(any("**How this works**" in text.value for text in app.markdown))
        self.assertTrue(any("privacy@example.com" in text.value for text in app.caption))


if __name__ == "__main__":
    unittest.main()
