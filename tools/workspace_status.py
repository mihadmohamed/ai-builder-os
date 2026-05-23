from __future__ import annotations

from common import (
    active_approvals,
    active_agent_threads,
    active_experience_findings,
    active_pm_clarifications,
    iter_projects,
    parse_requirements,
    parse_tasks,
    validate_project_structure,
)


def main() -> int:
    project_dirs = iter_projects()
    if not project_dirs:
        print("No projects found.")
        return 1

    print("AI Builder OS Workspace Status")
    print()
    print(f"projects: {len(project_dirs)}")
    print()

    failures = 0

    for project_dir in project_dirs:
        requirements = parse_requirements(project_dir / "product" / "requirements.md")
        tasks = parse_tasks(project_dir / "product" / "tasks.md")
        findings = active_experience_findings(project_dir / "data" / "experience_findings.json")
        clarifications = active_pm_clarifications(project_dir / "data" / "pm_clarifications.json")
        agent_threads = active_agent_threads(project_dir / "data" / "agent_threads.json")
        approvals = active_approvals(project_dir / "data" / "approvals.json")
        missing = validate_project_structure(project_dir)
        new_requirements = [item for item in requirements if item["status"] == "NEW"]

        print(f"PROJECT {project_dir.name}")
        print(
            f"  structure: {'PASS' if not missing else 'FAIL'}"
        )
        if missing:
            failures += 1
            for relative_path in missing:
                print(f"    missing: {relative_path}")

        print(f"  requirements: {len(requirements)}")
        if new_requirements:
            print(f"  new requirements: {len(new_requirements)}")
            for item in new_requirements:
                print(f"    - {item['id']}: {item['title']}")
        else:
            print("  new requirements: 0")

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
            print("  workflow artifacts:")
            for item in findings[:3]:
                print(
                    f"    - {item['finding_id']} [{item['handoff_state']}] -> {item['recommended_next_role']}: {item['recommendation_type']}"
                )

        print(f"  tasks: {len(tasks)}")
        if tasks:
            pending_tasks = [item for item in tasks if item["status"] != "DONE"]
            print(f"  pending tasks: {len(pending_tasks)}")
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
            print(f"  requirements ready to close: {len(ready_to_close)}")
            for item in ready_to_close:
                print(f"    - {item['id']}: {item['title']}")

        print()

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
