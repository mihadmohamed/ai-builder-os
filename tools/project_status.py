from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from common import (
    active_approvals,
    active_agent_threads,
    active_experience_findings,
    active_pm_clarifications,
    iter_projects,
    parse_requirements,
    parse_tasks,
)


def print_project_status(project_dir: Path) -> None:
    requirements = parse_requirements(project_dir / "product" / "requirements.md")
    tasks = parse_tasks(project_dir / "product" / "tasks.md")
    findings = active_experience_findings(project_dir / "data" / "experience_findings.json")
    clarifications = active_pm_clarifications(project_dir / "data" / "pm_clarifications.json")
    agent_threads = active_agent_threads(project_dir / "data" / "agent_threads.json")
    approvals = active_approvals(project_dir / "data" / "approvals.json")
    status_counts = Counter(item["status"] for item in requirements)

    print(f"PROJECT {project_dir.name}")
    print(f"  requirements: {len(requirements)}")
    if requirements:
        for status in sorted(status_counts):
            print(f"    {status}: {status_counts[status]}")
    else:
        print("    none found")

    new_requirements = [item for item in requirements if item["status"] == "NEW"]
    if new_requirements:
        print("  new requirements:")
        for item in new_requirements:
            print(f"    - {item['id']}: {item['title']}")

    print(f"  open approvals: {len(approvals)}")
    if approvals:
        print("  approval requests:")
        for item in approvals[:3]:
            print(f"    - {item['source_agent_name']} [{item['approval_type']}]: {item['title']}")

    print(f"  active pm clarifications: {len(clarifications)}")
    if clarifications:
        print("  clarification requests:")
        for item in clarifications[:3]:
            target = item.get("requirement_id") or item.get("requirement_title") or "PM discovery"
            print(f"    - {target} [{item['status']}]: {item['summary']}")

    print(f"  active agent threads: {len(agent_threads)}")
    if agent_threads:
        print("  active thread work:")
        for item in agent_threads[:3]:
            print(
                f"    - {item['agent_name']} / {item['mode']} [{item['status']}] last_role={item['last_role']}"
            )

    print(f"  active experience findings: {len(findings)}")
    if findings:
        finding_state_counts = Counter(item["handoff_state"] for item in findings)
        for state in sorted(finding_state_counts):
            print(f"    {state}: {finding_state_counts[state]}")
        print("  workflow artifacts:")
        for item in findings[:3]:
            print(
                f"    - {item['finding_id']} [{item['handoff_state']}] -> {item['recommended_next_role']}: {item['recommendation_type']}"
            )

    print(f"  tasks: {len(tasks)}")
    if tasks:
        task_status_counts = Counter(item["status"] for item in tasks)
        for status in sorted(task_status_counts):
            print(f"    {status}: {task_status_counts[status]}")

        pending_tasks = [item for item in tasks if item["status"] != "DONE"]
        if pending_tasks:
            print("  pending tasks:")
            for item in pending_tasks[:3]:
                print(f"    - {item['id']} [{item['status']}]: {item['title']}")

        latest_tasks = tasks[-3:]
        print("  latest tasks:")
        for item in latest_tasks:
            print(f"    - {item['id']} [{item['status']}]: {item['title']}")

    ready_to_close = []
    for requirement in requirements:
        if requirement["status"] != "IN_PROGRESS":
            continue
        linked_tasks = [task for task in tasks if requirement["id"] in task.get("requirements", [])]
        if linked_tasks and all(task["status"] == "DONE" for task in linked_tasks):
            ready_to_close.append(requirement)

    if ready_to_close:
        print("  requirements ready to close:")
        for item in ready_to_close:
            print(f"    - {item['id']}: {item['title']}")
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show a compact status summary for AI Builder OS projects."
    )
    parser.add_argument(
        "projects",
        nargs="*",
        help="Optional project names to summarize. Defaults to all projects.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    project_dirs = iter_projects(args.projects)
    if not project_dirs:
        print("No matching projects found.")
        return 1

    for project_dir in project_dirs:
        print_project_status(project_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
