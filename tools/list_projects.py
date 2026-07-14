from __future__ import annotations

from common import iter_projects


def main() -> int:
    project_dirs = iter_projects()
    if not project_dirs:
        print("No projects found.")
        return 0

    for project_dir in project_dirs:
        print(project_dir.name)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
