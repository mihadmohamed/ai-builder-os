from __future__ import annotations

import argparse

try:
    from tools.project_registry import discover_embedded_projects, load_project_manifest, write_project_manifest
except ModuleNotFoundError:  # Direct execution from tools/.
    from project_registry import discover_embedded_projects, load_project_manifest, write_project_manifest


def migrate_embedded_manifests(*, dry_run: bool = False) -> list[str]:
    changed: list[str] = []
    for location in discover_embedded_projects():
        if load_project_manifest(location.workspace_path) is not None:
            continue
        changed.append(location.name)
        if not dry_run:
            write_project_manifest(location)
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Add stable AI Builder OS manifests to embedded projects.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    changed = migrate_embedded_manifests(dry_run=args.dry_run)
    for name in changed:
        print(f"{'WOULD MIGRATE' if args.dry_run else 'MIGRATED'} {name}")
    print(f"SUMMARY: {len(changed)} project(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
