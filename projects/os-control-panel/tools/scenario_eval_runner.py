from __future__ import annotations

import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
TOOLS_ROOT = REPO_ROOT / "tools"
SCENARIOS_FILE = PROJECT_ROOT / "evals" / "scenarios.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

import orchestrator_status  # noqa: E402
import workspace  # noqa: E402


@dataclass(frozen=True)
class ScenarioFixture:
    scenario_id: str
    title: str
    description: str
    expected: dict[str, str]


@dataclass(frozen=True)
class ScenarioResult:
    fixture: ScenarioFixture
    passed: bool
    detail: str


def _load_fixtures() -> list[ScenarioFixture]:
    raw_items = json.loads(SCENARIOS_FILE.read_text())
    fixtures: list[ScenarioFixture] = []
    for item in raw_items:
        fixtures.append(
            ScenarioFixture(
                scenario_id=str(item["id"]),
                title=str(item["title"]),
                description=str(item["description"]),
                expected={str(key): str(value) for key, value in dict(item.get("expected", {})).items()},
            )
        )
    return fixtures


def _requirements_markdown(active: list[dict[str, str]], backlog: list[dict[str, str]] | None = None) -> str:
    backlog = backlog or []
    lines = ["# Product Requirements", "", "## Active Requirements", ""]
    for item in active:
        lines.extend(
            [
                f"### {item['id']} — {item['title']}",
                "",
                f"Status: {item['status']}",
                f"Priority: {item.get('priority', 'MEDIUM')}",
                f"Effort: {item.get('effort', 'M')}",
                "Description:",
                item.get("description", "Scenario fixture requirement."),
                "",
            ]
        )
    lines.extend(["---", "", "## Backlog (Not yet prioritised)", ""])
    for item in backlog:
        lines.extend(
            [
                f"### {item['id']} — {item['title']}",
                "",
                f"Status: {item['status']}",
                f"Priority: {item.get('priority', 'MEDIUM')}",
                f"Effort: {item.get('effort', 'M')}",
                "Description:",
                item.get("description", "Scenario fixture requirement."),
                "",
            ]
        )
    lines.extend(["---", "", "## Rules", "", "- Keep this scenario deterministic.", ""])
    return "\n".join(lines)


def _create_project_dir(root: Path, name: str, requirements_text: str, tasks_text: str = "# Product Tasks\n") -> Path:
    project_dir = root / name
    (project_dir / "product").mkdir(parents=True, exist_ok=True)
    (project_dir / "data").mkdir(parents=True, exist_ok=True)
    (project_dir / "product" / "requirements.md").write_text(requirements_text)
    (project_dir / "product" / "tasks.md").write_text(tasks_text)
    (project_dir / "data" / "experience_findings.json").write_text("[]")
    (project_dir / "data" / "pm_clarifications.json").write_text("[]")
    return project_dir


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _scenario_new_requirement_routes_to_pm(fixture: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = _create_project_dir(
            Path(temp_dir),
            "scenario-project",
            _requirements_markdown(
                [
                    {
                        "id": "R21",
                        "title": "Add scenario coverage",
                        "status": "NEW",
                        "priority": "HIGH",
                        "effort": "S",
                    }
                ]
            ),
        )
        decision = orchestrator_status._decision_for_project(project_dir)
        _assert(decision.next_role == fixture.expected["next_role"], f"Expected {fixture.expected['next_role']}, got {decision.next_role}")
        return decision.why


def _scenario_open_clarification_blocks_with_product_director(fixture: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = _create_project_dir(
            Path(temp_dir),
            "scenario-project",
            _requirements_markdown(
                [
                    {
                        "id": "R22",
                        "title": "Add background sync control",
                        "status": "NEW",
                    }
                ]
            ),
        )
        (project_dir / "data" / "pm_clarifications.json").write_text(
            json.dumps(
                [
                    {
                        "clarification_id": "c-open",
                        "project_name": "scenario-project",
                        "requirement_id": "R22",
                        "requirement_title": "Add background sync control",
                        "summary": "Clarify whether the one-at-a-time rule applies per project or globally.",
                        "questions": [
                            "Should the one-background-sync rule apply per project or across the whole OS?"
                        ],
                        "status": "OPEN",
                        "created_at": "2026-04-25T10:00:00+00:00",
                    }
                ],
                indent=2,
            )
        )
        decision = orchestrator_status._decision_for_project(project_dir)
        _assert(decision.next_role == fixture.expected["next_role"], f"Expected {fixture.expected['next_role']}, got {decision.next_role}")
        return decision.why


def _scenario_routed_experience_finding_routes_to_pm(fixture: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = _create_project_dir(
            Path(temp_dir),
            "scenario-project",
            _requirements_markdown(
                [
                    {
                        "id": "R23",
                        "title": "Keep the dashboard tidy",
                        "status": "DONE",
                    }
                ]
            ),
        )
        (project_dir / "data" / "experience_findings.json").write_text(
            json.dumps(
                [
                    {
                        "finding_id": "f-routed",
                        "project_name": "scenario-project",
                        "user_problem": "The workspace cards feel cluttered.",
                        "recommendation_type": "UX improvement in scope",
                        "recommended_next_role": "PM",
                        "handoff_state": "routed",
                        "created_at": "2026-04-25T10:00:00+00:00",
                    }
                ],
                indent=2,
            )
        )
        decision = orchestrator_status._decision_for_project(project_dir)
        _assert(decision.next_role == fixture.expected["next_role"], f"Expected {fixture.expected['next_role']}, got {decision.next_role}")
        return decision.why


def _scenario_requirement_deletion_cleans_linked_state(_: ScenarioFixture) -> str:
    source_requirements = REPO_ROOT / "projects" / "os-control-panel" / "product" / "requirements.md"
    source_tasks = REPO_ROOT / "projects" / "os-control-panel" / "product" / "tasks.md"
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        temp_requirements = temp_root / "requirements.md"
        temp_requirements.write_text(
            source_requirements.read_text().replace(
                "\n---\n\n## Rules",
                "\n\n### R99 — Scenario deletion target\n\nStatus: BACKLOG\nPriority: LOW\nEffort: S\nDescription:\nTemporary requirement for scenario deletion eval.\n\n---\n\n## Rules",
                1,
            )
        )
        temp_tasks = temp_root / "tasks.md"
        temp_tasks.write_text(
            source_tasks.read_text()
            + "\n\n## Task 99: Requirement-specific follow-up\n\nType: Feature Task\nStatus: TODO\nRequirement: R99\n\nGoal:\nKeep requirement-specific work.\n"
            + "\n\n## Task 100: Shared follow-up\n\nType: Feature Task\nStatus: TODO\nRequirements: R99, R17\n\nGoal:\nKeep shared work.\n"
        )
        temp_pm_clarifications = temp_root / "pm_clarifications.json"
        temp_pm_clarifications.write_text(
            '[{"clarification_id":"c1","project_name":"os-control-panel","requirement_id":"R99","requirement_title":"Extra","summary":"Clarify","questions":["Q1"],"status":"OPEN","created_at":"2026-04-25T00:00:00+00:00"}]'
        )
        temp_runs = temp_root / "implementation_runs.json"
        temp_output = temp_root / "run-output.txt"
        temp_output.write_text("summary")
        temp_log = temp_root / "run.log"
        temp_log.write_text("log")
        temp_runs.write_text(
            f'[{{"run_id":"run1","project_name":"os-control-panel","requirement_id":"R99","requirement_title":"Extra","status":"COMPLETED","summary":"","error":"","created_at":"","started_at":"","finished_at":"","output_path":"{temp_output}","log_path":"{temp_log}","worker_pid":null}}]'
        )

        with patch("workspace._requirements_path", return_value=temp_requirements), patch(
            "workspace._tasks_path", return_value=temp_tasks
        ), patch("workspace._pm_clarifications_path", return_value=temp_pm_clarifications), patch(
            "workspace.IMPLEMENTATION_FILE", temp_runs
        ):
            deleted = workspace.delete_requirement("os-control-panel", "R99")
            updated = workspace.load_requirement_document("os-control-panel")
            task_text = temp_tasks.read_text()

        ids = [record.id for record in updated.active_requirements + updated.backlog_requirements]
        _assert("R99" not in ids, "Deleted requirement should be removed from requirements.md.")
        _assert("## Task 99: Requirement-specific follow-up" not in task_text, "Single-requirement task should be removed.")
        _assert("Requirement: R17" in task_text, "Shared task should retain the surviving linked requirement.")
        _assert(deleted.removed_clarifications == 1, "Linked PM clarification should be removed.")
        _assert(deleted.removed_implementation_runs == 1, "Linked implementation run should be removed.")
        _assert(not temp_output.exists(), "Implementation output artifact should be deleted.")
        _assert(not temp_log.exists(), "Implementation log artifact should be deleted.")
        return "Deleted requirement cleaned linked tasks, clarifications, and implementation artifacts."


def _scenario_implementation_lock_is_project_scoped(_: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        temp_file = temp_root / "implementation_runs.json"
        temp_file.write_text("[]")
        temp_log_dir = temp_root / "logs"

        with patch("workspace.IMPLEMENTATION_FILE", temp_file), patch(
            "workspace.IMPLEMENTATION_LOG_DIR", temp_log_dir
        ), patch("workspace.subprocess.Popen") as mock_popen, patch(
            "workspace._worker_process_alive", return_value=True
        ):
            mock_popen.return_value.pid = 4321
            first = workspace.RequirementRecord("R15", "Allow initiation", "IN_PROGRESS", "HIGH", "L", "desc")
            second = workspace.RequirementRecord("R1", "Parentmate flow", "NEW", "HIGH", "M", "desc")
            first_run = workspace.start_requirement_implementation("os-control-panel", first)
            second_run = workspace.start_requirement_implementation("parentmate", second)

            _assert(
                workspace.active_implementation_run("os-control-panel").run_id == first_run.run_id,
                "First project should keep its own active run.",
            )
            _assert(
                workspace.active_implementation_run("parentmate").run_id == second_run.run_id,
                "Second project should be allowed to start its own run.",
            )
        return "Different projects can hold independent active implementation runs."


def _scenario_pm_chat_discovery_produces_draft(_: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_threads = Path(temp_dir) / "agent_threads.json"
        temp_threads.write_text("[]")
        turn_count = {"value": 0}

        def fake_live_pm_turn(*_: object, **__: object) -> workspace.LivePMTurn:
            turn_count["value"] += 1
            if turn_count["value"] >= 6:
                return workspace.LivePMTurn(
                    next_action="draft_requirements",
                    assistant_message="I have enough context to draft this requirement.",
                    draft_title="Add PM chat workspace",
                    draft_requirement=(
                        "Problem statement\n"
                        "- The PM discovery flow feels too much like a form.\n\n"
                        "Target user\n"
                        "- Product Director inside a project.\n\n"
                        "Core job-to-be-done\n"
                        "- Shape feature ideas through a conversational PM flow.\n\n"
                        "Success criteria\n"
                        "- PM asks relevant follow-up questions and saves a structured draft.\n\n"
                        "Constraints\n"
                        "- Keep it clean and local-first.\n\n"
                        "Out of scope\n"
                        "- Full multi-agent chat.\n\n"
                        "Assumptions\n"
                        "- A lightweight active thread is enough.\n\n"
                        "Open questions\n"
                        "- None for this scenario."
                    ),
                )
            return workspace.LivePMTurn(
                next_action="ask_question",
                assistant_message="What should PM clarify next?",
            )

        with patch("workspace.AGENT_THREAD_FILE", temp_threads), patch(
            "workspace._run_live_pm_turn", side_effect=fake_live_pm_turn
        ):
            thread = workspace.start_pm_requirement_discovery_thread(
                "os-control-panel",
                "I want a real PM chat flow inside the project page.",
            )
            for answer in (
                "The Product Director inside a project.",
                "The current flow feels too much like a form.",
                "This shows up while shaping new feature ideas.",
                "Keep it clean and local-first.",
                "It should feel conversational and still save a structured draft.",
            ):
                thread = workspace.reply_to_pm_requirement_discovery_thread(
                    "os-control-panel",
                    thread.thread_id,
                    answer,
                )

            _assert(thread.draft.strip() != "", "PM chat should produce a non-empty draft.")
            _assert("Problem statement" in thread.draft, "Draft should include the structured PM output sections.")
        return "PM chat gathered enough context and produced a structured draft."


def _scenario_active_pm_thread_routes_to_product_director(fixture: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = _create_project_dir(
            Path(temp_dir),
            "scenario-project",
            _requirements_markdown(
                [
                    {
                        "id": "R24",
                        "title": "Add PM chat workspace",
                        "status": "DONE",
                    }
                ]
            ),
        )
        (project_dir / "data" / "agent_threads.json").write_text(
            json.dumps(
                [
                    {
                        "thread_id": "thread-1",
                        "project_name": "scenario-project",
                        "agent_name": "PM",
                        "mode": "Requirement Discovery",
                        "status": "active",
                        "idea": "I want PM to help shape a requirement.",
                        "draft": "",
                        "messages": [
                            {"role": "user", "content": "Help me shape a requirement.", "created_at": "2026-04-30T10:00:00+00:00"},
                            {"role": "assistant", "content": "Who is the primary user?", "created_at": "2026-04-30T10:00:05+00:00"},
                        ],
                        "updated_at": "2026-04-30T10:00:05+00:00",
                    }
                ],
                indent=2,
            )
        )
        decision = orchestrator_status._decision_for_project(project_dir)
        _assert(decision.next_role == fixture.expected["next_role"], f"Expected {fixture.expected['next_role']}, got {decision.next_role}")
        return decision.why


def _scenario_structural_pending_task_routes_to_architect(fixture: ScenarioFixture) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = _create_project_dir(
            Path(temp_dir),
            "scenario-project",
            _requirements_markdown(
                [
                    {
                        "id": "R25",
                        "title": "Add background worker for project execution",
                        "status": "IN_PROGRESS",
                        "priority": "HIGH",
                        "effort": "L",
                        "description": "Introduce a background worker and new execution workflow artifact for project runs.",
                    }
                ]
            ),
            tasks_text=(
                "# Product Tasks\n\n"
                "## Task 1: Add worker-backed execution path\n\n"
                "Type: Feature Task\n"
                "Status: TODO\n"
                "Requirement: R25\n\n"
                "Goal:\n"
                "Implement the execution path.\n"
            ),
        )
        decision = orchestrator_status._decision_for_project(project_dir)
        _assert(decision.next_role == fixture.expected["next_role"], f"Expected {fixture.expected['next_role']}, got {decision.next_role}")
        return decision.why


SCENARIO_HANDLERS: dict[str, Callable[[ScenarioFixture], str]] = {
    "new_requirement_routes_to_pm": _scenario_new_requirement_routes_to_pm,
    "open_clarification_blocks_with_product_director": _scenario_open_clarification_blocks_with_product_director,
    "routed_experience_finding_routes_to_pm": _scenario_routed_experience_finding_routes_to_pm,
    "requirement_deletion_cleans_linked_state": _scenario_requirement_deletion_cleans_linked_state,
    "implementation_lock_is_project_scoped": _scenario_implementation_lock_is_project_scoped,
    "pm_chat_discovery_produces_draft": _scenario_pm_chat_discovery_produces_draft,
    "active_pm_thread_routes_to_product_director": _scenario_active_pm_thread_routes_to_product_director,
    "structural_pending_task_routes_to_architect": _scenario_structural_pending_task_routes_to_architect,
}


def run_scenarios() -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    for fixture in _load_fixtures():
        handler = SCENARIO_HANDLERS.get(fixture.scenario_id)
        if handler is None:
            results.append(
                ScenarioResult(
                    fixture=fixture,
                    passed=False,
                    detail=f"No handler implemented for scenario `{fixture.scenario_id}`.",
                )
            )
            continue
        try:
            detail = handler(fixture)
        except Exception as exc:
            results.append(ScenarioResult(fixture=fixture, passed=False, detail=str(exc)))
            continue
        results.append(ScenarioResult(fixture=fixture, passed=True, detail=detail))
    return results


def main() -> int:
    results = run_scenarios()
    passed = sum(1 for item in results if item.passed)
    total = len(results)
    for item in results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status} {item.fixture.scenario_id} — {item.fixture.title}")
        print(f"  {item.detail}")
    print(f"SCENARIO SUMMARY: {passed}/{total} passing")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
