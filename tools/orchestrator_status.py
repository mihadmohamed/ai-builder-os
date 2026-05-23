from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from common import (
    active_approvals,
    active_agent_threads,
    active_experience_findings,
    active_pm_clarifications,
    iter_projects,
    parse_requirements,
    parse_tasks,
    requirement_has_experience_trigger,
    requirement_has_structural_trigger,
    requirement_has_ui_trigger,
)


ACTIVE_FINDING_STATES = {
    "ready_for_pm_review",
    "ready_for_product_director",
    "handoff_prepared",
    "routed",
}


@dataclass(frozen=True)
class OrchestratorDecision:
    next_action: str
    next_role: str
    why: str


def _resolve_project_dir(project_name: str) -> Path:
    matches = iter_projects([project_name])
    if not matches:
        raise ValueError(f"Project not found: {project_name}")
    return matches[0]


def _decision_for_project(project_dir: Path) -> OrchestratorDecision:
    requirements = parse_requirements(project_dir / "product" / "requirements.md")
    tasks = parse_tasks(project_dir / "product" / "tasks.md")
    findings = active_experience_findings(project_dir / "data" / "experience_findings.json")
    clarifications = active_pm_clarifications(project_dir / "data" / "pm_clarifications.json")
    agent_threads = active_agent_threads(project_dir / "data" / "agent_threads.json")
    approvals = active_approvals(project_dir / "data" / "approvals.json")

    if approvals:
        first = approvals[0]
        return OrchestratorDecision(
            next_action=f"Review approval request: {first['title']}.",
            next_role="Product Director",
            why=f"{first['source_agent_name']} created an open approval request that should be resolved before the workflow progresses.",
        )

    if clarifications:
        first = clarifications[0]
        target = first.get("requirement_id") or first.get("requirement_title") or "PM discovery"
        return OrchestratorDecision(
            next_action=f"Answer PM clarification for {target}.",
            next_role="Product Director",
            why=f"{target} has an open PM clarification request that should be resolved before further tasking or implementation.",
        )

    if agent_threads:
        thread = agent_threads[0]
        agent_name = str(thread.get("agent_name", "Agent"))
        mode = str(thread.get("mode", ""))
        last_role = str(thread.get("last_role", ""))
        if last_role == "assistant":
            return OrchestratorDecision(
                next_action=f"Continue the active {agent_name} {mode} thread in the project UI.",
                next_role="Product Director",
                why=f"Thread {thread['thread_id']} is still active and currently waiting on a human reply before the workflow can progress.",
            )
        return OrchestratorDecision(
            next_action=f"Continue the active {agent_name} {mode} thread.",
            next_role=agent_name or "PM",
            why=f"Thread {thread['thread_id']} is still active and should complete before the project is treated as idle.",
        )

    new_requirements = [item for item in requirements if item["status"] == "NEW"]
    if new_requirements:
        if len(new_requirements) == 1:
            item = new_requirements[0]
            return OrchestratorDecision(
                next_action=f"Run PM on {item['id']}.",
                next_role="PM",
                why=f"{item['id']} is marked NEW in product/requirements.md and has not yet been turned into tasks.",
            )
        ids = ", ".join(item["id"] for item in new_requirements)
        return OrchestratorDecision(
            next_action="Run PM prioritisation on the NEW requirements.",
            next_role="PM",
            why=f"Multiple requirements are NEW ({ids}), so PM should prioritise and normally activate one requirement at a time.",
        )

    if findings:
        routed = next((item for item in findings if item["handoff_state"] == "routed"), None)
        if routed is not None:
            role = routed["recommended_next_role"] or "PM"
            return OrchestratorDecision(
                next_action=f"Run {role} on the routed workflow artifact.",
                next_role=role,
                why=f"Finding {routed['finding_id']} is routed and points to {role}.",
            )

        ready_pm = next((item for item in findings if item["handoff_state"] == "ready_for_pm_review"), None)
        if ready_pm is not None:
            return OrchestratorDecision(
                next_action="Run PM on the ready-for-review experience finding.",
                next_role="PM",
                why=f"Finding {ready_pm['finding_id']} is waiting on PM review.",
            )

        ready_pd = next((item for item in findings if item["handoff_state"] == "ready_for_product_director"), None)
        if ready_pd is not None:
            return OrchestratorDecision(
                next_action="Review the scope-escalation finding with the Product Director.",
                next_role="Product Director",
                why=f"Finding {ready_pd['finding_id']} is waiting on Product Director review.",
            )

        prepared = next((item for item in findings if item["handoff_state"] == "handoff_prepared"), None)
        if prepared is not None:
            role = prepared["recommended_next_role"] or "PM"
            return OrchestratorDecision(
                next_action="Complete the prepared handoff and then run the recommended role.",
                next_role=role,
                why=f"Finding {prepared['finding_id']} is handoff_prepared and should be handed off intentionally before the next role acts.",
            )

    pending_tasks = [item for item in tasks if item["status"] in {"TODO", "IN_PROGRESS"}]
    if pending_tasks:
        first = pending_tasks[0]
        requirement_by_id = {item["id"]: item for item in requirements}
        linked_requirements = [requirement_by_id[req_id] for req_id in first.get("requirements", []) if req_id in requirement_by_id]
        if any(requirement_has_structural_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorDecision(
                next_action=f"Run Architect review before implementation on {linked_ids}.",
                next_role="Architect",
                why=f"{first['id']} is pending, but its linked requirement introduces a structural trigger that should be reviewed before Engineer starts.",
            )
        if any(requirement_has_experience_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorDecision(
                next_action=f"Run Experience Designer before implementation on {linked_ids}.",
                next_role="Experience Designer",
                why=f"{first['id']} is pending, and its linked requirement is experience-heavy enough that usability/workflow review should happen before Engineer starts.",
            )
        if any(requirement_has_ui_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorDecision(
                next_action=f"Run UI Designer before implementation on {linked_ids}.",
                next_role="UI Designer",
                why=f"{first['id']} is pending, and its linked requirement is UI-heavy enough that design direction or UI review should happen before Engineer starts.",
            )
        return OrchestratorDecision(
            next_action=f"Run Engineer on {first['id']}.",
            next_role="Engineer",
            why=f"{first['id']} is still {first['status']} in product/tasks.md.",
        )

    ready_to_close = []
    for requirement in requirements:
        if requirement["status"] != "IN_PROGRESS":
            continue
        linked = [task for task in tasks if requirement["id"] in task.get("requirements", [])]
        if linked and all(task["status"] == "DONE" for task in linked):
            ready_to_close.append(requirement)

    if ready_to_close:
        item = ready_to_close[0]
        return OrchestratorDecision(
            next_action=f"Close {item['id']} in requirements.md.",
            next_role="None",
            why=f"{item['id']} is still IN_PROGRESS but all linked tasks are DONE.",
        )

    backlog = [item for item in requirements if item["status"] == "BACKLOG"]
    if backlog:
        return OrchestratorDecision(
            next_action="No agent needs to run automatically.",
            next_role="None",
            why="There are no NEW requirements, no active workflow artifacts, and no pending tasks. Remaining work is backlog only.",
        )

    return OrchestratorDecision(
        next_action="No agent needs to run automatically.",
        next_role="None",
        why="There are no NEW requirements, no active workflow artifacts, and no pending tasks.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compute the next orchestration step for an AI Builder OS project from full file state."
    )
    parser.add_argument("project_name", help="Project name under projects/")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    project_dir = _resolve_project_dir(args.project_name)
    decision = _decision_for_project(project_dir)

    print(f"PROJECT {project_dir.name}")
    print(f"NEXT_ACTION {decision.next_action}")
    print(f"NEXT_ROLE {decision.next_role}")
    print(f"WHY {decision.why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
