from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[4]
TOOLS_ROOT = REPO_ROOT / "tools"
SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"
for candidate in (str(REPO_ROOT), str(TOOLS_ROOT), str(SRC_ROOT)):
    if candidate not in os.sys.path:
        os.sys.path.insert(0, candidate)

from control_plane import WorkflowController
from control_plane.storage import control_data_dir
import workspace
from tools.create_project import scaffold_project
from tools.project_registry import ProjectLocation, list_project_locations, load_project_manifest, register_project, resolve_project
from tools.project_repositories import (
    attach_repository,
    plan_attached_repository,
    plan_standalone_repository,
    publish_standalone_repository,
)


class ProjectRegistryTests(unittest.TestCase):
    def _environment(self, temp_dir: str):
        root = Path(temp_dir)
        return patch.dict(
            os.environ,
            {
                "AI_BUILDER_OS_PROJECT_REGISTRY": str(root / "registry.json"),
                "AI_BUILDER_OS_RUNTIME_ROOT": str(root / "runtime"),
            },
            clear=False,
        )

    def test_embedded_projects_have_stable_manifests(self) -> None:
        location = resolve_project("os-control-panel")
        self.assertEqual(location.mode, "embedded_showcase")
        self.assertEqual(location.visibility, "public")
        self.assertTrue(location.project_id)
        self.assertEqual(load_project_manifest(location.workspace_path), location)

    def test_registers_and_resolves_external_project_by_id_or_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, self._environment(temp_dir):
            workspace_parent = Path(temp_dir) / "workspaces"
            destination = scaffold_project(
                "private-client-app",
                display_name="Private Client App",
                initial_requirement="Build the first private workflow.",
                workspace_parent=workspace_parent,
                project_id=str(uuid4()),
                mode="managed_standalone",
                visibility="private",
                ownership="client",
                repository="owner/private-client-app",
            )
            manifest = load_project_manifest(destination)
            self.assertIsNotNone(manifest)
            registered = register_project(manifest, write_manifest=False)  # type: ignore[arg-type]

            self.assertEqual(resolve_project(registered.project_id), registered)
            self.assertEqual(resolve_project("private-client-app"), registered)
            self.assertIn(registered, list_project_locations())

            registry = json.loads((Path(temp_dir) / "registry.json").read_text())
            self.assertEqual(registry["projects"][0]["workspace_path"], str(destination))

    def test_control_plane_uses_external_canonical_files_and_stable_runtime_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, self._environment(temp_dir):
            destination = scaffold_project(
                "external-control-test",
                display_name="External Control Test",
                initial_requirement="Keep canonical truth in this repository.",
                workspace_parent=Path(temp_dir) / "workspaces",
                project_id=str(uuid4()),
                mode="attached_repository",
                visibility="private",
                ownership="self",
                repository="owner/external-control-test",
            )
            location = load_project_manifest(destination)
            self.assertIsNotNone(location)
            register_project(location, write_manifest=False)  # type: ignore[arg-type]

            snapshot = WorkflowController().snapshot("external-control-test")

            self.assertEqual(snapshot["project_id"], location.project_id)  # type: ignore[union-attr]
            self.assertTrue(snapshot["project_location"]["external"])
            self.assertEqual(snapshot["project_location"]["repository"], "")
            runtime = control_data_dir("external-control-test")
            self.assertIn(location.project_id, runtime.parts)  # type: ignore[union-attr]
            self.assertNotIn("external-control-test", runtime.parts)

    def test_rejects_external_workspace_nested_inside_embedded_projects(self) -> None:
        nested = REPO_ROOT / "projects" / "nested-external-test"
        location = ProjectLocation(
            project_id=str(uuid4()),
            name="nested-external-test",
            display_name="Nested External Test",
            mode="managed_standalone",
            workspace_path=nested,
            visibility="private",
            ownership="self",
            repository="owner/nested-external-test",
        )
        with self.assertRaisesRegex(ValueError, "must not be nested"):
            register_project(location)

    def test_standalone_plan_defaults_private_and_publish_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = plan_standalone_repository(
                project_name="new-product",
                workspace_parent=Path(temp_dir),
                repository="owner/new-product",
            )
            self.assertEqual(plan.visibility, "private")
            self.assertIn("Create a private GitHub repository", plan.external_side_effects)
            with self.assertRaisesRegex(PermissionError, "explicit approval"):
                publish_standalone_repository(plan, approved=False)

    def test_attached_repository_writes_manifest_and_registers_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir, self._environment(temp_dir):
            workspace = Path(temp_dir) / "existing-client-app"
            (workspace / ".git").mkdir(parents=True)
            (workspace / "product").mkdir()
            (workspace / "product" / "requirements.md").write_text("# Requirements\n", encoding="utf-8")

            plan = plan_attached_repository(
                workspace_path=workspace,
                repository="owner/existing-client-app",
                ownership="client",
            )
            registered = attach_repository(plan, display_name="Existing Client App")

            self.assertEqual(registered.mode, "attached_repository")
            self.assertEqual(registered.visibility, "private")
            self.assertEqual(resolve_project(registered.project_id), registered)
            self.assertEqual(load_project_manifest(workspace), registered)

    def test_attached_repository_rejects_invalid_visibility_before_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir) / "existing-app"
            (workspace / ".git").mkdir(parents=True)
            (workspace / "product").mkdir()
            (workspace / "product" / "requirements.md").write_text("# Requirements\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "visibility"):
                plan_attached_repository(
                    workspace_path=workspace,
                    repository="owner/existing-app",
                    visibility="internal",
                )

    def test_os_control_panel_release_plan_covers_repo_wide_public_changes(self) -> None:
        with patch(
            "workspace._git_status_paths",
            return_value=(
                "tools/project_registry.py",
                "plugins/ai-builder-os/.codex-plugin/plugin.json",
                "private/ai-builder-os/projects.json",
            ),
        ), patch("workspace._git_deleted_paths", return_value=()), patch(
            "workspace._current_git_branch", return_value="feature"
        ):
            plan = workspace._release_git_change_plan("os-control-panel")

        self.assertIn("tools/project_registry.py", plan.included_paths)
        self.assertIn("plugins/ai-builder-os/.codex-plugin/plugin.json", plan.included_paths)
        self.assertIn("private/ai-builder-os/projects.json", plan.excluded_paths)

    def test_release_plan_allows_deleting_a_normally_blocked_public_path(self) -> None:
        removed_path = "projects/retired-showcase/data/imported-public-asset.png"
        with patch("workspace._git_status_paths", return_value=(removed_path,)), patch(
            "workspace._git_deleted_paths", return_value=(removed_path,)
        ), patch("workspace._current_git_branch", return_value="feature"):
            plan = workspace._release_git_change_plan("os-control-panel")

        self.assertIn(removed_path, plan.included_paths)
        self.assertNotIn(removed_path, plan.excluded_paths)

    def test_release_commit_keeps_approved_deletion_of_blocked_path(self) -> None:
        removed_path = "projects/retired-showcase/data/imported-public-asset.png"
        with patch("workspace._git_deleted_paths", return_value=(removed_path,)), patch(
            "workspace._staged_git_paths", return_value=()
        ), patch("workspace._run_git_command") as run_git, patch("workspace.subprocess.run"):
            result = workspace._commit_and_push_release(
                "os-control-panel",
                {"git_included_paths": removed_path},
            )

        run_git.assert_called_once_with("os-control-panel", ["add", "-u", "--", removed_path])
        self.assertIn("No staged changes", result["git_delivery_detail"])

    def test_release_commit_does_not_restage_an_approved_staged_deletion(self) -> None:
        removed_path = "projects/retired-showcase/data/imported-public-asset.png"
        with patch("workspace._git_deleted_paths", return_value=(removed_path,)), patch(
            "workspace._staged_git_paths", return_value=(removed_path,)
        ), patch("workspace._run_git_command") as run_git, patch("workspace.subprocess.run"):
            result = workspace._commit_and_push_release(
                "os-control-panel",
                {"git_included_paths": removed_path},
            )

        run_git.assert_not_called()
        self.assertIn("No staged changes", result["git_delivery_detail"])

    def test_release_commit_skips_absent_source_of_an_approved_staged_rename(self) -> None:
        renamed_source = "projects/retired-showcase/product/desktop.png"
        renamed_destination = "showcases/retired-showcase/desktop.png"
        with patch("workspace._git_deleted_paths", return_value=()), patch(
            "workspace._staged_git_paths", return_value=(renamed_destination,)
        ), patch("workspace._run_git_command") as run_git, patch("workspace.subprocess.run"):
            result = workspace._commit_and_push_release(
                "os-control-panel",
                {"git_included_paths": f"{renamed_source}\n{renamed_destination}"},
            )

        run_git.assert_not_called()
        self.assertIn("No staged changes", result["git_delivery_detail"])


if __name__ == "__main__":
    unittest.main()
