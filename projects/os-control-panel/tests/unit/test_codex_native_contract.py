from __future__ import annotations

import os
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[4]


class CodexNativeContractTests(unittest.TestCase):
    def test_project_scoped_agents_are_narrow_and_valid(self) -> None:
        expected = {
            "orchestrator",
            "pm",
            "experience_designer",
            "ui_designer",
            "architect",
            "engineer",
            "qa",
            "learning_agent",
        }
        agent_dir = REPO_ROOT / ".codex" / "agents"
        configs = {path.stem: tomllib.loads(path.read_text(encoding="utf-8")) for path in agent_dir.glob("*.toml")}

        self.assertEqual(set(configs), expected)
        for filename, config in configs.items():
            self.assertTrue(config["name"])
            self.assertTrue(config["description"])
            self.assertTrue(config["developer_instructions"])
            expected_sandbox = "workspace-write" if filename == "engineer" else "read-only"
            self.assertEqual(config["sandbox_mode"], expected_sandbox)

    def test_project_config_bounds_subagent_fanout(self) -> None:
        config = tomllib.loads((REPO_ROOT / ".codex" / "config.toml").read_text(encoding="utf-8"))
        self.assertLessEqual(config["agents"]["max_threads"], 4)
        self.assertEqual(config["agents"]["max_depth"], 1)

    def test_skill_makes_codex_native_default_and_sdk_explicit(self) -> None:
        text = (REPO_ROOT / ".agents" / "skills" / "ai-builder-os-workflow" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Keep model work in the current Codex chat by default", text)
        self.assertIn("only when the user explicitly asks", text)
        self.assertNotIn("Call `start_agent_workflow` when the user wants", text)

    def test_api_agents_are_disabled_by_default(self) -> None:
        from app import _api_agents_enabled

        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_api_agents_enabled())
        with patch.dict(os.environ, {"AI_BUILDER_OS_ENABLE_API_AGENTS": "1"}, clear=True):
            self.assertTrue(_api_agents_enabled())

    def test_native_ui_path_has_no_agents_sdk_call(self) -> None:
        app_text = (REPO_ROOT / "projects" / "os-control-panel" / "src" / "app.py").read_text(encoding="utf-8")
        native_body = app_text.split("def render_codex_workflow", 1)[1].split("def render_sdk_agent_workflow", 1)[0]
        self.assertIn("create_codex_work_request", native_body)
        self.assertNotIn("_agents_sdk_runtime", native_body)
        self.assertNotIn("AgentsWorkflowRuntime", native_body)


if __name__ == "__main__":
    unittest.main()
