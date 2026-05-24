from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
SHOWCASE_ROOT = REPO_ROOT / "showcase"

if str(SHOWCASE_ROOT) not in sys.path:
    sys.path.insert(0, str(SHOWCASE_ROOT))

import app  # noqa: E402


class ShowcaseAppTests(unittest.TestCase):
    def test_showcase_sections_are_stable(self) -> None:
        self.assertEqual(app.showcase_sections(), ("Overview", "Workflow", "Projects", "Try It"))

    def test_showcase_projects_cover_workspace_examples(self) -> None:
        project_names = [project.name for project in app.showcase_projects()]
        self.assertEqual(
            project_names,
            ["OS Control Panel", "ParentMate", "Personal Trip Planner"],
        )

    def test_github_project_url_targets_project_folder(self) -> None:
        project = app.showcase_projects()[0]
        self.assertEqual(
            app.github_project_url(project),
            "https://github.com/mihadmohamed/ai-builder-os/tree/main/projects/os-control-panel",
        )

    def test_github_repo_url_can_be_overridden_for_public_repo(self) -> None:
        with patch.dict(os.environ, {"AI_BUILDER_OS_PUBLIC_REPO_URL": "https://github.com/example/ai-builder-os"}, clear=False):
            project = app.showcase_projects()[1]
            self.assertEqual(app.github_repo_url(), "https://github.com/example/ai-builder-os")
            self.assertEqual(
                app.github_project_url(project),
                "https://github.com/example/ai-builder-os/tree/main/projects/parentmate",
            )

    def test_try_it_commands_include_showcase_entrypoint(self) -> None:
        commands = app.try_it_commands()
        self.assertIn('PYTHONPATH="$PWD" .venv/bin/streamlit run showcase/app.py', commands["Run the public showcase"])


if __name__ == "__main__":
    unittest.main()
