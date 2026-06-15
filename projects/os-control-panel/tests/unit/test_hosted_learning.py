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
                self.assertTrue(any("Admitted learner" in text.value for text in app.markdown))
                self.assertTrue(any("Learning plan" in text.value for text in app.markdown))

    def test_admitted_landing_prioritizes_profile_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    workspace.RUNTIME_ROOT_ENV: temp_dir,
                    "LEARNING_AGENT_AUTH_MODE": "local",
                    "LEARNING_AGENT_LOCAL_USER": "admitted@example.com",
                },
            ):
                app = AppTest.from_file(
                    str(REPO_ROOT / "projects" / "learning-agent" / "src" / "app.py"),
                    default_timeout=30,
                ).run()

        self.assertTrue(any("Welcome back, Local User" in text.value for text in app.markdown))
        self.assertTrue(any("1 · Profile" in text.value for text in app.markdown))
        self.assertTrue(any("2 · Learning plan" in text.value for text in app.markdown))
        self.assertTrue(any("3 · Learn next" in text.value for text in app.markdown))
        self.assertTrue(any("Signed in as admitted@example.com" in text.value for text in app.caption))
        self.assertTrue(any("Learning profile" in text.value for text in app.markdown))
        self.assertFalse(any(text.value == "### Pilot boundary" for text in app.markdown))
        self.assertTrue(any(expander.label == "Edit learning profile" for expander in app.expander))

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
        self.assertIn("width=320", source)
        self.assertEqual(source.count("with st.container(border=True):"), 2)

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
        self.assertTrue(any("How it works" in text.value for text in app.markdown))
        self.assertTrue(any("privacy@example.com" in text.value for text in app.caption))

    def test_non_approved_user_can_submit_access_request(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    workspace.RUNTIME_ROOT_ENV: temp_dir,
                    "AI_BUILDER_OS_RUNTIME_ROOT": temp_dir,
                    "LEARNING_AGENT_AUTH_MODE": "local",
                    "LEARNING_AGENT_PRIVACY_CONTACT": "privacy@example.com",
                    "LEARNING_AGENT_ALLOWED_EMAILS": "approved@example.com",
                    "LEARNING_AGENT_LOCAL_USER": "pending@example.com",
                },
            ):
                app = AppTest.from_file(
                    str(REPO_ROOT / "projects" / "learning-agent" / "src" / "app.py"),
                    default_timeout=30,
                ).run()

                self.assertTrue(any("Request access" in text.value for text in app.markdown))
                self.assertTrue(any("Learn how AI Builder OS works" in text.value for text in app.markdown))
                self.assertTrue(any("Preview account" in text.value for text in app.caption))
                self.assertFalse(app.info)
                self.assertTrue(any(button.label == "Enlarge preview" for button in app.button))
                app.text_area(key="learning-agent-access-note").set_value("I want to evaluate the learning flow for pilot onboarding.")
                next(button for button in app.button if button.label == "Request access").click().run()

                request_log = Path(temp_dir) / "learning-agent-access-requests.jsonl"
                self.assertTrue(request_log.exists())
                payload = request_log.read_text(encoding="utf-8")
                self.assertIn("pending@example.com", payload)
                self.assertIn("pilot onboarding", payload)
                self.assertTrue(any("Request received" in element.value for element in app.success))

    def test_non_approved_user_can_open_learning_preview_dialog(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    workspace.RUNTIME_ROOT_ENV: temp_dir,
                    "AI_BUILDER_OS_RUNTIME_ROOT": temp_dir,
                    "LEARNING_AGENT_AUTH_MODE": "local",
                    "LEARNING_AGENT_ALLOWED_EMAILS": "approved@example.com",
                    "LEARNING_AGENT_LOCAL_USER": "pending@example.com",
                },
            ):
                app = AppTest.from_file(
                    str(REPO_ROOT / "projects" / "learning-agent" / "src" / "app.py"),
                    default_timeout=30,
                ).run()

                next(button for button in app.button if button.label == "Enlarge preview").click().run()

                self.assertTrue(
                    any("Live tutoring unlocks after admission" in caption.value for caption in app.caption)
                )


if __name__ == "__main__":
    unittest.main()
