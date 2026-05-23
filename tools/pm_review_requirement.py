from __future__ import annotations

import argparse
from pathlib import Path

from common import PROJECTS_ROOT, create_pm_clarification, parse_requirements


def _requirements_path(project_name: str) -> Path:
    return PROJECTS_ROOT / project_name / "product" / "requirements.md"


def _clarification_path(project_name: str) -> Path:
    return PROJECTS_ROOT / project_name / "data" / "pm_clarifications.json"


def _find_requirement(project_name: str, requirement_id: str) -> dict[str, str]:
    requirements = parse_requirements(_requirements_path(project_name))
    match = next((item for item in requirements if item["id"] == requirement_id), None)
    if match is None:
        raise ValueError(f"Requirement not found: {requirement_id}")
    return match


def _raw_requirement_text(project_name: str, requirement_id: str) -> str:
    text = _requirements_path(project_name).read_text()
    marker = f"### {requirement_id} —"
    start = text.find(marker)
    if start == -1:
        return ""
    next_start = text.find("\n### R", start + len(marker))
    if next_start == -1:
        next_start = text.find("\n---", start + len(marker))
    if next_start == -1:
        next_start = len(text)
    return text[start:next_start]


def detect_questions(raw_text: str) -> list[str]:
    lowered = raw_text.lower()
    questions: list[str] = []

    if "only one" in lowered or "one at a time" in lowered:
        questions.append(
            "What is the intended unit of the one-at-a-time rule: per requirement, per project, per workspace, per user, or global?"
        )

    if "active" in lowered and "implementation" in lowered and "project" not in lowered and "workspace" not in lowered:
        questions.append(
            "Does this execution constraint apply within one project only, or should it affect other projects too?"
        )

    if any(keyword in lowered for keyword in ("workflow", "orchestrator", "background", "worker", "runtime")):
        questions.append(
            "What workflow or runtime boundaries should PM make explicit before tasking this requirement?"
        )

    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a narrow PM ambiguity scan for one requirement.")
    parser.add_argument("project_name")
    parser.add_argument("requirement_id")
    args = parser.parse_args()

    requirement = _find_requirement(args.project_name, args.requirement_id)
    raw_text = _raw_requirement_text(args.project_name, args.requirement_id)
    questions = detect_questions(raw_text)

    print(f"PROJECT {args.project_name}")
    print(f"REQUIREMENT {args.requirement_id}")

    if not questions:
        print("RESULT CLEAR_ENOUGH")
        print("WHY No high-risk ambiguity pattern was detected by the lightweight PM review helper.")
        return 0

    clarification = create_pm_clarification(
        _clarification_path(args.project_name),
        project_name=args.project_name,
        requirement_id=args.requirement_id,
        requirement_title=requirement["title"],
        summary="PM clarification required before task generation or implementation can proceed.",
        questions=questions,
    )
    print("RESULT CLARIFICATION_CREATED")
    print(f"CLARIFICATION {clarification['clarification_id']}")
    for question in clarification["questions"]:
        print(f"- {question}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
