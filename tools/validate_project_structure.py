from __future__ import annotations

import argparse

from common import iter_projects, validate_project_structure


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate AI Builder OS project structure."
    )
    parser.add_argument(
        "projects",
        nargs="*",
        help="Optional project names to validate. Defaults to all projects.",
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
        missing = validate_project_structure(project_dir)
        if missing:
            failures += 1
            print(f"FAIL {project_dir.name}")
            for relative_path in missing:
                print(f"  missing: {relative_path}")
        else:
            print(f"PASS {project_dir.name}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
