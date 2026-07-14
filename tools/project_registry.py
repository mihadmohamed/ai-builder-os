from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable, Literal
from uuid import NAMESPACE_URL, uuid5


PROJECT_MANIFEST_VERSION = 1
PROJECT_REGISTRY_VERSION = 1
PROJECT_MANIFEST_DIR = ".ai-builder-os"
PROJECT_MANIFEST_NAME = "project.json"

ProjectMode = Literal["embedded_showcase", "managed_standalone", "attached_repository"]
RepositoryVisibility = Literal["public", "private"]
RepositoryOwnership = Literal["self", "client", "organisation"]


@dataclass(frozen=True)
class ProjectLocation:
    project_id: str
    name: str
    display_name: str
    mode: ProjectMode
    workspace_path: Path
    visibility: RepositoryVisibility
    ownership: RepositoryOwnership
    repository: str = ""
    default_branch: str = "main"

    @property
    def manifest_path(self) -> Path:
        return self.workspace_path / PROJECT_MANIFEST_DIR / PROJECT_MANIFEST_NAME

    @property
    def is_external(self) -> bool:
        return self.mode != "embedded_showcase"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def embedded_projects_root() -> Path:
    return _repo_root() / "projects"


def registry_path() -> Path:
    configured = os.getenv("AI_BUILDER_OS_PROJECT_REGISTRY", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    home = os.getenv("AI_BUILDER_OS_HOME", "").strip()
    base = Path(home).expanduser().resolve() if home else _repo_root() / "private" / "ai-builder-os"
    return base / "projects.json"


def stable_embedded_project_id(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"ai-builder-os:embedded:{name}"))


def _validate_slug(value: str, field: str) -> str:
    clean = value.strip()
    if not clean or clean in {".", ".."} or "/" in clean or "\\" in clean:
        raise ValueError(f"{field} must be a non-empty project slug")
    return clean


def _validate_enum(value: str, allowed: set[str], field: str) -> str:
    clean = value.strip().lower()
    if clean not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")
    return clean


def _validate_repository(value: str) -> str:
    clean = value.strip()
    if not clean:
        return ""
    parts = clean.split("/")
    if len(parts) != 2 or any(not part or part in {".", ".."} for part in parts):
        raise ValueError("repository must use owner/name format")
    return clean


def _manifest_payload(location: ProjectLocation) -> dict[str, object]:
    return {
        "version": PROJECT_MANIFEST_VERSION,
        "project_id": location.project_id,
        "name": location.name,
        "display_name": location.display_name,
        "mode": location.mode,
        "visibility": location.visibility,
        "ownership": location.ownership,
        "repository": location.repository,
        "default_branch": location.default_branch,
    }


def write_project_manifest(location: ProjectLocation) -> Path:
    path = location.manifest_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_manifest_payload(location), indent=2) + "\n", encoding="utf-8")
    return path


def load_project_manifest(project_root: Path) -> ProjectLocation | None:
    root = project_root.expanduser().resolve()
    path = root / PROJECT_MANIFEST_DIR / PROJECT_MANIFEST_NAME
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("version", 0)) != PROJECT_MANIFEST_VERSION:
        raise ValueError(f"Unsupported project manifest version: {path}")
    return ProjectLocation(
        project_id=_validate_slug(str(payload.get("project_id", "")), "project_id"),
        name=_validate_slug(str(payload.get("name", "")), "name"),
        display_name=str(payload.get("display_name", "")).strip() or str(payload.get("name", "")),
        mode=_validate_enum(
            str(payload.get("mode", "")),
            {"embedded_showcase", "managed_standalone", "attached_repository"},
            "mode",
        ),  # type: ignore[arg-type]
        workspace_path=root,
        visibility=_validate_enum(
            str(payload.get("visibility", "")), {"public", "private"}, "visibility"
        ),  # type: ignore[arg-type]
        ownership=_validate_enum(
            str(payload.get("ownership", "")), {"self", "client", "organisation"}, "ownership"
        ),  # type: ignore[arg-type]
        repository=_validate_repository(str(payload.get("repository", ""))),
        default_branch=_validate_slug(str(payload.get("default_branch", "main")), "default_branch"),
    )


def _registry_payload(locations: Iterable[ProjectLocation]) -> dict[str, object]:
    return {
        "version": PROJECT_REGISTRY_VERSION,
        "projects": [
            {
                **{key: value for key, value in asdict(item).items() if key != "workspace_path"},
                "workspace_path": str(item.workspace_path),
            }
            for item in sorted(locations, key=lambda value: value.project_id)
        ],
    }


def _atomic_write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def load_registered_projects() -> list[ProjectLocation]:
    path = registry_path()
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if int(payload.get("version", 0)) != PROJECT_REGISTRY_VERSION:
        raise ValueError(f"Unsupported project registry version: {path}")
    raw_projects = payload.get("projects", [])
    if not isinstance(raw_projects, list):
        raise ValueError(f"Invalid project registry: {path}")
    locations: list[ProjectLocation] = []
    seen_ids: set[str] = set()
    seen_paths: set[Path] = set()
    for raw in raw_projects:
        if not isinstance(raw, dict):
            raise ValueError(f"Invalid project registry entry: {raw!r}")
        root = Path(str(raw.get("workspace_path", ""))).expanduser().resolve()
        manifest = load_project_manifest(root)
        if manifest is None:
            raise ValueError(f"Registered project is missing its manifest: {root}")
        registered_id = _validate_slug(str(raw.get("project_id", "")), "project_id")
        if manifest.project_id != registered_id:
            raise ValueError(f"Registry and manifest project IDs disagree: {root}")
        if registered_id in seen_ids or root in seen_paths:
            raise ValueError(f"Duplicate project registry entry: {registered_id}")
        seen_ids.add(registered_id)
        seen_paths.add(root)
        locations.append(manifest)
    return locations


def discover_embedded_projects() -> list[ProjectLocation]:
    root = embedded_projects_root()
    if not root.is_dir():
        return []
    discovered: list[ProjectLocation] = []
    for project_root in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda item: item.name):
        if not (project_root / "product" / "requirements.md").is_file():
            continue
        manifest = load_project_manifest(project_root)
        if manifest is not None:
            if manifest.mode != "embedded_showcase":
                raise ValueError(f"Embedded project manifest has external mode: {manifest.manifest_path}")
            discovered.append(manifest)
            continue
        name = project_root.name
        discovered.append(
            ProjectLocation(
                project_id=stable_embedded_project_id(name),
                name=name,
                display_name=name.replace("-", " ").replace("_", " ").title(),
                mode="embedded_showcase",
                workspace_path=project_root.resolve(),
                visibility="public",
                ownership="self",
                repository="mihadmohamed/ai-builder-os",
            )
        )
    return discovered


def list_project_locations() -> list[ProjectLocation]:
    by_id: dict[str, ProjectLocation] = {}
    active_root = os.getenv("AI_BUILDER_OS_ACTIVE_PROJECT_ROOT", "").strip()
    active_manifest = load_project_manifest(
        Path(active_root).expanduser().resolve() if active_root else Path.cwd().resolve()
    )
    active = [active_manifest] if active_manifest is not None else []
    for item in discover_embedded_projects() + load_registered_projects() + active:
        existing = by_id.get(item.project_id)
        if existing is not None and existing.workspace_path != item.workspace_path:
            if existing.name != item.name:
                raise ValueError(f"Project ID is registered with conflicting names: {item.project_id}")
            if existing.mode == "embedded_showcase" and item.is_external:
                by_id[item.project_id] = item
                continue
            if existing.is_external and item.mode == "embedded_showcase":
                continue
            raise ValueError(f"Project ID is registered at multiple paths: {item.project_id}")
        by_id[item.project_id] = item
    return sorted(by_id.values(), key=lambda item: (item.display_name.lower(), item.name))


def resolve_project(project_ref: str) -> ProjectLocation:
    clean = project_ref.strip()
    matches = [
        item
        for item in list_project_locations()
        if clean in {item.project_id, item.name} or clean.lower() == item.display_name.lower()
    ]
    if not matches:
        raise ValueError(f"Unknown project: {project_ref}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous project reference; use the stable project ID: {project_ref}")
    return matches[0]


def register_project(location: ProjectLocation, *, write_manifest: bool = True) -> ProjectLocation:
    root = location.workspace_path.expanduser().resolve()
    embedded_root = embedded_projects_root().resolve()
    if root == embedded_root or embedded_root in root.parents:
        raise ValueError("Standalone and attached repositories must not be nested inside AI Builder OS projects/")
    normalized = ProjectLocation(
        project_id=_validate_slug(location.project_id, "project_id"),
        name=_validate_slug(location.name, "name"),
        display_name=location.display_name.strip() or location.name,
        mode=_validate_enum(
            location.mode, {"managed_standalone", "attached_repository"}, "mode"
        ),  # type: ignore[arg-type]
        workspace_path=root,
        visibility=_validate_enum(location.visibility, {"public", "private"}, "visibility"),  # type: ignore[arg-type]
        ownership=_validate_enum(
            location.ownership, {"self", "client", "organisation"}, "ownership"
        ),  # type: ignore[arg-type]
        repository=_validate_repository(location.repository),
        default_branch=_validate_slug(location.default_branch, "default_branch"),
    )
    if not root.is_dir():
        raise ValueError(f"Project workspace does not exist: {root}")
    if not (root / "product" / "requirements.md").is_file():
        raise ValueError(f"Project workspace is missing product/requirements.md: {root}")
    if write_manifest:
        write_project_manifest(normalized)
    elif load_project_manifest(root) is None:
        raise ValueError(f"Project workspace is missing its manifest: {root}")
    registered = load_registered_projects()
    embedded = discover_embedded_projects()
    for existing in embedded + registered:
        if existing.name == normalized.name and existing.project_id != normalized.project_id:
            raise ValueError(f"Project name is already registered: {normalized.name}")
    for existing in registered:
        if existing.project_id == normalized.project_id and existing.workspace_path != root:
            raise ValueError(f"Project ID is already registered: {normalized.project_id}")
        if existing.workspace_path == root and existing.project_id != normalized.project_id:
            raise ValueError(f"Workspace path is already registered: {root}")
    updated = [item for item in registered if item.project_id != normalized.project_id]
    updated.append(normalized)
    _atomic_write(registry_path(), _registry_payload(updated))
    return normalized


def unregister_project(project_ref: str) -> ProjectLocation:
    target = resolve_project(project_ref)
    if not target.is_external:
        raise ValueError("Embedded projects are discovered from the repository and cannot be unregistered")
    registered = load_registered_projects()
    remaining = [item for item in registered if item.project_id != target.project_id]
    _atomic_write(registry_path(), _registry_payload(remaining))
    return target
