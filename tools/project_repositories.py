from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import subprocess
from uuid import uuid4

try:
    from tools.create_project import scaffold_project
    from tools.project_registry import ProjectLocation, load_project_manifest, register_project, write_project_manifest
except ModuleNotFoundError:  # Direct execution from tools/.
    from create_project import scaffold_project
    from project_registry import ProjectLocation, load_project_manifest, register_project, write_project_manifest


@dataclass(frozen=True)
class RepositoryActionPlan:
    action: str
    project_id: str
    project_name: str
    workspace_path: str
    repository: str
    visibility: str
    ownership: str
    default_branch: str
    external_side_effects: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _repository_slug(value: str) -> str:
    clean = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", clean):
        raise ValueError("repository must use GitHub owner/name format")
    return clean


def plan_standalone_repository(
    *,
    project_name: str,
    workspace_parent: Path,
    repository: str,
    visibility: str = "private",
    ownership: str = "self",
    default_branch: str = "main",
    project_id: str = "",
) -> RepositoryActionPlan:
    normalized_visibility = visibility.strip().lower() or "private"
    if normalized_visibility not in {"private", "public"}:
        raise ValueError("visibility must be private or public")
    normalized_ownership = ownership.strip().lower() or "self"
    if normalized_ownership not in {"self", "client", "organisation"}:
        raise ValueError("ownership must be self, client, or organisation")
    name = re.sub(r"[^a-z0-9]+", "-", project_name.strip().lower()).strip("-")
    if not name:
        raise ValueError("project_name must not be empty")
    parent = workspace_parent.expanduser().resolve()
    return RepositoryActionPlan(
        action="create_standalone_repository",
        project_id=project_id.strip() or str(uuid4()),
        project_name=name,
        workspace_path=str(parent / name),
        repository=_repository_slug(repository),
        visibility=normalized_visibility,
        ownership=normalized_ownership,
        default_branch=default_branch.strip() or "main",
        external_side_effects=(
            f"Create a {normalized_visibility} GitHub repository",
            "Push the scaffolded project and canonical product history",
            "Register the local workspace with AI Builder OS",
        ),
    )


def scaffold_standalone_repository(
    plan: RepositoryActionPlan,
    *,
    display_name: str,
    initial_requirement_title: str,
    initial_requirement: str,
    ui_runtime: str,
) -> ProjectLocation:
    if plan.action != "create_standalone_repository":
        raise ValueError(f"Unsupported plan action: {plan.action}")
    destination = scaffold_project(
        plan.project_name,
        display_name=display_name,
        product_title=display_name,
        initial_requirement_title=initial_requirement_title,
        initial_requirement=initial_requirement,
        ui_runtime=ui_runtime,
        workspace_parent=Path(plan.workspace_path).parent,
        project_id=plan.project_id,
        mode="managed_standalone",
        visibility=plan.visibility,
        ownership=plan.ownership,
        repository=plan.repository,
        default_branch=plan.default_branch,
    )
    location = load_project_manifest(destination)
    if location is None:
        raise RuntimeError(f"Standalone scaffold did not produce a project manifest: {destination}")
    return register_project(location, write_manifest=False)


def plan_attached_repository(
    *,
    workspace_path: Path,
    repository: str,
    visibility: str = "private",
    ownership: str = "self",
    default_branch: str = "main",
    project_id: str = "",
) -> RepositoryActionPlan:
    root = workspace_path.expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Attached workspace does not exist: {root}")
    if not (root / ".git").exists():
        raise ValueError(f"Attached workspace is not a Git repository: {root}")
    if not (root / "product" / "requirements.md").is_file():
        raise ValueError(f"Attached workspace is not an AI Builder OS project: {root}")
    normalized_visibility = visibility.strip().lower() or "private"
    if normalized_visibility not in {"private", "public"}:
        raise ValueError("visibility must be private or public")
    normalized_ownership = ownership.strip().lower() or "self"
    if normalized_ownership not in {"self", "client", "organisation"}:
        raise ValueError("ownership must be self, client, or organisation")
    name = root.name
    return RepositoryActionPlan(
        action="attach_repository",
        project_id=project_id.strip() or str(uuid4()),
        project_name=name,
        workspace_path=str(root),
        repository=_repository_slug(repository),
        visibility=normalized_visibility,
        ownership=normalized_ownership,
        default_branch=default_branch.strip() or "main",
        external_side_effects=("Write the project manifest", "Register the local workspace with AI Builder OS"),
    )


def attach_repository(plan: RepositoryActionPlan, *, display_name: str) -> ProjectLocation:
    if plan.action != "attach_repository":
        raise ValueError(f"Unsupported plan action: {plan.action}")
    location = ProjectLocation(
        project_id=plan.project_id,
        name=plan.project_name,
        display_name=display_name.strip() or plan.project_name,
        mode="attached_repository",
        workspace_path=Path(plan.workspace_path),
        visibility=plan.visibility,  # type: ignore[arg-type]
        ownership=plan.ownership,  # type: ignore[arg-type]
        repository=plan.repository,
        default_branch=plan.default_branch,
    )
    write_project_manifest(location)
    return register_project(location, write_manifest=False)


def _run_git(args: list[str], *, cwd: Path) -> None:
    completed = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown git error"
        raise RuntimeError(detail)


def publish_standalone_repository(plan: RepositoryActionPlan, *, approved: bool) -> dict[str, str]:
    if not approved:
        raise PermissionError("GitHub repository creation requires explicit approval")
    root = Path(plan.workspace_path).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Standalone workspace does not exist: {root}")
    if not (root / ".git").exists():
        _run_git(["git", "init", "-b", plan.default_branch], cwd=root)
    _run_git(["git", "add", "."], cwd=root)
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, check=False
    )
    if status.returncode != 0:
        raise RuntimeError(status.stderr.strip() or "Unable to inspect standalone Git state")
    if status.stdout.strip():
        _run_git(["git", "commit", "-m", "Initialize project with AI Builder OS"], cwd=root)
    remote = subprocess.run(
        ["git", "remote", "get-url", "origin"], cwd=root, capture_output=True, text=True, check=False
    )
    if remote.returncode == 0 and remote.stdout.strip():
        _run_git(["git", "push", "--set-upstream", "origin", plan.default_branch], cwd=root)
        return {
            "repository": plan.repository,
            "visibility": plan.visibility,
            "url": f"https://github.com/{plan.repository}",
            "detail": "Pushed the approved standalone workspace to its existing origin.",
        }
    exists = subprocess.run(
        ["gh", "repo", "view", plan.repository, "--json", "nameWithOwner"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if exists.returncode == 0:
        _run_git(["git", "remote", "add", "origin", f"https://github.com/{plan.repository}.git"], cwd=root)
        _run_git(["git", "push", "--set-upstream", "origin", plan.default_branch], cwd=root)
        return {
            "repository": plan.repository,
            "visibility": plan.visibility,
            "url": f"https://github.com/{plan.repository}",
            "detail": "Connected and pushed to the existing approved GitHub repository.",
        }
    command = [
        "gh",
        "repo",
        "create",
        plan.repository,
        f"--{plan.visibility}",
        "--source",
        str(root),
        "--remote",
        "origin",
        "--push",
    ]
    completed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown GitHub error"
        raise RuntimeError(detail)
    return {
        "repository": plan.repository,
        "visibility": plan.visibility,
        "url": f"https://github.com/{plan.repository}",
        "detail": completed.stdout.strip(),
    }


def save_repository_action_plan(path: Path, plan: RepositoryActionPlan) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path
