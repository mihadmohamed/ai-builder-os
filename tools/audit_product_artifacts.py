from __future__ import annotations

import argparse
from pathlib import Path

from common import find_orphan_product_artifacts, iter_projects


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit project product artifacts and report files under product/ that "
            "are not referenced from canonical requirements/tasks registries."
        )
    )
    parser.add_argument(
        "projects",
        nargs="*",
        help="Optional project names to audit. Defaults to all projects.",
    )
    return parser
def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    project_dirs = iter_projects(args.projects)
    if not project_dirs:
        print("No matching projects found.")
        return 1

    failures = 0
    for project_dir in project_dirs:
        orphans = find_orphan_product_artifacts(project_dir)
        relative_project = Path(project_dir.name)
        if orphans:
            failures += 1
            print(f"FAIL {relative_project}")
            for orphan in orphans:
                print(f"  orphan artifact: {orphan}")
        else:
            print(f"PASS {relative_project}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
