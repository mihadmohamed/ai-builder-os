from __future__ import annotations

from datetime import datetime, timezone
import ast
import re
import json
from pathlib import Path
from uuid import uuid4


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECTS_ROOT = REPO_ROOT / "projects"
TEMPLATE_ROOT = REPO_ROOT / "templates" / "project"

TEXT_FILE_SUFFIXES = {
    ".md",
    ".txt",
    ".py",
    ".json",
    ".toml",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".gitignore",
}

REQUIRED_PROJECT_PATHS = [
    "README.md",
    "memory.md",
    "rules.md",
    "product/requirements.md",
    "product/tasks.md",
    "src",
    "evals",
    "tools",
    "tests",
    "data",
]

REQUIREMENT_HEADER_PATTERN = re.compile(r"^###\s+(R\d+)\s+—\s+(.+)$")
STATUS_PATTERN = re.compile(r"^Status:\s+(.+)$")
TASK_HEADER_PATTERN = re.compile(r"^##\s+Task\s+(\d+):\s+(.+)$")
TASK_STATUS_PATTERN = re.compile(r"^Status:\s+(.+)$")
TASK_REQUIREMENT_PATTERN = re.compile(r"^Requirement(?:s)?:\s+(.+)$")
REQUIREMENT_BLOCK_PATTERN = re.compile(
    r"###\s+(R\d+)\s+—\s+(.+?)\n\n"
    r"Status:\s+(.+?)\n"
    r"(?:Priority:\s+(.+?)\n)?"
    r"(?:Effort:\s+(.+?)\n)?"
    r"Description:\n"
    r"(.*?)(?=\n###\s+R\d+\s+—|\n---|\Z)",
    re.DOTALL,
)
REQUIREMENT_ID_PATTERN = re.compile(r"\bR\d+\b")
ACTIVE_EXPERIENCE_HANDOFF_STATES = {
    "ready_for_pm_review",
    "ready_for_product_director",
    "handoff_prepared",
    "routed",
}
ACTIVE_PM_CLARIFICATION_STATES = {"OPEN"}
ACTIVE_AGENT_THREAD_STATES = {"active"}
ACTIVE_APPROVAL_STATES = {"OPEN"}
STRUCTURAL_TRIGGER_KEYWORDS = {
    "runtime",
    "execution",
    "worker",
    "background",
    "concurrency",
    "queue",
    "persistence",
    "workflow artifact",
    "workflow-artifact",
    "orchestration",
    "source of truth",
    "source-of-truth",
    "cross-project",
    "shared infrastructure",
    "sandbox",
    "security",
    "trust boundary",
    "agent workspace",
    "agent-thread",
    "agent thread",
}
UI_TRIGGER_KEYWORDS = {
    "ui",
    "user interface",
    "visual",
    "layout",
    "spacing",
    "hierarchy",
    "color",
    "colour",
    "typography",
    "aesthetic",
    "look and feel",
    "design polish",
    "polish",
    "screen",
    "page",
    "card",
    "component",
}
EXPERIENCE_TRIGGER_KEYWORDS = {
    "usability",
    "workflow",
    "friction",
    "clarity",
    "confusing",
    "confusion",
    "discoverability",
    "scan",
    "scanability",
    "noisy",
    "overwhelming",
    "navigation",
    "user problem",
    "onboarding",
    "feedback",
    "comprehension",
}


def iter_projects(selected_projects: list[str] | None = None) -> list[Path]:
    if not PROJECTS_ROOT.exists():
        return []

    available = {path.name: path for path in PROJECTS_ROOT.iterdir() if path.is_dir()}
    if selected_projects:
        return [available[name] for name in selected_projects if name in available]

    return sorted(available.values())


def project_display_name(project_name: str) -> str:
    words = project_name.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words) or project_name


def normalize_project_directory_name(project_name: str) -> str:
    lowered = project_name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "project"


def should_treat_as_text(path: Path) -> bool:
    return path.suffix in TEXT_FILE_SUFFIXES or path.name in {
        "README",
        "README.md",
        ".gitkeep",
    }


def validate_project_structure(project_dir: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in REQUIRED_PROJECT_PATHS:
        if not (project_dir / relative_path).exists():
            missing.append(relative_path)
    return missing


def find_orphan_product_artifacts(project_dir: Path) -> list[str]:
    product_dir = project_dir / "product"
    if not product_dir.exists():
        return []

    canonical_text_parts: list[str] = []
    for name in ("requirements.md", "tasks.md"):
        path = product_dir / name
        canonical_text_parts.append(path.read_text() if path.exists() else "")
    canonical_text = "\n".join(canonical_text_parts)

    orphans: list[str] = []
    for artifact_path in sorted(product_dir.glob("*.md")):
        if artifact_path.name in {"requirements.md", "tasks.md"}:
            continue
        if artifact_path.name not in canonical_text:
            orphans.append(str(artifact_path.relative_to(REPO_ROOT)))
    return orphans


def audit_learning_agent_wrapper() -> list[str]:
    issues: list[str] = []

    wrapper_app = PROJECTS_ROOT / "learning-agent" / "src" / "app.py"
    wrapper_readme = PROJECTS_ROOT / "learning-agent" / "README.md"
    control_panel_readme = PROJECTS_ROOT / "os-control-panel" / "README.md"

    if not wrapper_app.exists():
        return [str(wrapper_app.relative_to(REPO_ROOT)) + " is missing"]

    source = wrapper_app.read_text()

    try:
        tree = ast.parse(source, filename=str(wrapper_app))
    except SyntaxError as exc:
        return [f"{wrapper_app.relative_to(REPO_ROOT)} has invalid syntax: {exc.msg}"]

    imports_render_learning_tab = False
    imports_workspace = False
    imports_render_learning_tab_name = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "app":
                imported_names = {alias.name for alias in node.names}
                if "render_learning_tab" in imported_names:
                    imports_render_learning_tab = True
                    imports_render_learning_tab_name = True
            if node.module == "workspace":
                imports_workspace = True

    if not imports_render_learning_tab or not imports_render_learning_tab_name:
        issues.append(
            "projects/learning-agent/src/app.py must import `render_learning_tab` from the canonical "
            "`projects/os-control-panel/src/app.py` surface."
        )

    if imports_workspace:
        issues.append(
            "projects/learning-agent/src/app.py must not import directly from `workspace`; "
            "learning behavior should stay behind the canonical app surface."
        )

    if 'AI_BUILDER_OS_LEARNING_RELEASE_PROFILE", "external_v2"' not in source:
        issues.append(
            "projects/learning-agent/src/app.py must set the external V2 learning release profile."
        )

    if wrapper_readme.exists():
        readme_text = wrapper_readme.read_text()
        if "hosted wrapper" not in readme_text.lower():
            issues.append(
                "projects/learning-agent/README.md should describe the hosted app as a wrapper."
            )
        if "canonical source of truth" not in readme_text.lower():
            issues.append(
                "projects/learning-agent/README.md should point to os-control-panel as the canonical source of truth."
            )

    if control_panel_readme.exists():
        control_text = control_panel_readme.read_text()
        if "projects/learning-agent" not in control_text or "canonical source of truth for Learning Agent behavior" not in control_text:
            issues.append(
                "projects/os-control-panel/README.md should document the hosted-wrapper relationship."
            )

    return issues


def parse_requirements(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    text = path.read_text()
    block_matches = list(REQUIREMENT_BLOCK_PATTERN.finditer(text))
    if block_matches:
        requirements: list[dict[str, str]] = []
        for match in block_matches:
            requirements.append(
                {
                    "id": match.group(1).strip(),
                    "title": match.group(2).strip(),
                    "status": match.group(3).strip(),
                    "priority": (match.group(4) or "").strip(),
                    "effort": (match.group(5) or "").strip(),
                    "description": match.group(6).strip(),
                }
            )
        return requirements

    requirements: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        header_match = REQUIREMENT_HEADER_PATTERN.match(line)
        if header_match:
            current = {
                "id": header_match.group(1),
                "title": header_match.group(2).strip(),
                "status": "UNKNOWN",
                "priority": "",
                "effort": "",
                "description": "",
            }
            requirements.append(current)
            continue

        if current is None:
            continue

        status_match = STATUS_PATTERN.match(line)
        if status_match:
            current["status"] = status_match.group(1).strip()

    return requirements


def parse_tasks(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    tasks: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        match = TASK_HEADER_PATTERN.match(line)
        if match:
            current = {
                "id": f"Task {match.group(1)}",
                "title": match.group(2).strip(),
                "status": "UNKNOWN",
                "requirements": [],
            }
            tasks.append(current)
            continue

        if current is None:
            continue

        status_match = TASK_STATUS_PATTERN.match(line)
        if status_match:
            current["status"] = status_match.group(1).strip()
            continue

        requirement_match = TASK_REQUIREMENT_PATTERN.match(line)
        if requirement_match:
            current["requirements"] = REQUIREMENT_ID_PATTERN.findall(requirement_match.group(1))

    return tasks


def parse_experience_findings(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    try:
        raw_findings = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    findings: list[dict[str, str]] = []
    for item in raw_findings:
        if not isinstance(item, dict):
            continue
        findings.append(
            {
                "finding_id": str(item.get("finding_id", "")),
                "project_name": str(item.get("project_name", "")),
                "user_problem": str(item.get("user_problem", "")),
                "recommendation_type": str(item.get("recommendation_type", "")),
                "recommended_next_role": str(item.get("recommended_next_role", "")),
                "handoff_state": str(item.get("handoff_state", "")),
                "created_at": str(item.get("created_at", "")),
            }
        )
    return findings


def active_experience_findings(path: Path) -> list[dict[str, str]]:
    return [
        finding
        for finding in parse_experience_findings(path)
        if finding.get("handoff_state") in ACTIVE_EXPERIENCE_HANDOFF_STATES
    ]


def parse_pm_clarifications(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    try:
        raw_items = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    clarifications: list[dict[str, object]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        raw_questions = item.get("questions", [])
        questions = [str(question) for question in raw_questions] if isinstance(raw_questions, list) else []
        clarifications.append(
            {
                "clarification_id": str(item.get("clarification_id", "")),
                "project_name": str(item.get("project_name", "")),
                "requirement_id": str(item.get("requirement_id", "")),
                "requirement_title": str(item.get("requirement_title", "")),
                "source_thread_id": str(item.get("source_thread_id", "")),
                "summary": str(item.get("summary", "")),
                "questions": questions,
                "status": str(item.get("status", "")),
                "created_at": str(item.get("created_at", "")),
            }
        )
    return clarifications


def active_pm_clarifications(path: Path) -> list[dict[str, object]]:
    return [
        clarification
        for clarification in parse_pm_clarifications(path)
        if clarification.get("status") in ACTIVE_PM_CLARIFICATION_STATES
    ]


def parse_agent_threads(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    try:
        raw_items = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    threads: list[dict[str, object]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        raw_messages = item.get("messages", [])
        messages: list[dict[str, str]] = []
        if isinstance(raw_messages, list):
            for message in raw_messages:
                if not isinstance(message, dict):
                    continue
                messages.append(
                    {
                        "role": str(message.get("role", "")),
                        "content": str(message.get("content", "")),
                        "created_at": str(message.get("created_at", "")),
                    }
                )
        threads.append(
            {
                "thread_id": str(item.get("thread_id", "")),
                "project_name": str(item.get("project_name", "")),
                "agent_name": str(item.get("agent_name", "")),
                "mode": str(item.get("mode", "")),
                "status": str(item.get("status", "")),
                "idea": str(item.get("idea", "")),
                "draft": str(item.get("draft", "")),
                "last_role": messages[-1]["role"] if messages else "",
                "messages": messages,
                "updated_at": str(item.get("updated_at", "")),
            }
        )
    return threads


def active_agent_threads(path: Path) -> list[dict[str, object]]:
    return [
        thread
        for thread in parse_agent_threads(path)
        if thread.get("status") in ACTIVE_AGENT_THREAD_STATES
    ]


def parse_approvals(path: Path) -> list[dict[str, object]]:
    if not path.exists():
        return []

    try:
        raw_items = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    approvals: list[dict[str, object]] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        approvals.append(
            {
                "approval_id": str(item.get("approval_id", "")),
                "project_name": str(item.get("project_name", "")),
                "approval_type": str(item.get("approval_type", "")),
                "source_thread_id": str(item.get("source_thread_id", "")),
                "source_agent_name": str(item.get("source_agent_name", "")),
                "title": str(item.get("title", "")),
                "summary": str(item.get("summary", "")),
                "status": str(item.get("status", "")),
                "created_at": str(item.get("created_at", "")),
            }
        )
    return approvals


def active_approvals(path: Path) -> list[dict[str, object]]:
    return [
        approval
        for approval in parse_approvals(path)
        if approval.get("status") in ACTIVE_APPROVAL_STATES
    ]


def requirement_has_structural_trigger(requirement: dict[str, object]) -> bool:
    haystack = " ".join(
        [
            str(requirement.get("title", "")),
            str(requirement.get("description", "")),
        ]
    ).lower()
    return any(keyword in haystack for keyword in STRUCTURAL_TRIGGER_KEYWORDS)


def requirement_has_ui_trigger(requirement: dict[str, object]) -> bool:
    haystack = " ".join(
        [
            str(requirement.get("title", "")),
            str(requirement.get("description", "")),
        ]
    ).lower()
    return any(keyword in haystack for keyword in UI_TRIGGER_KEYWORDS)


def requirement_has_experience_trigger(requirement: dict[str, object]) -> bool:
    haystack = " ".join(
        [
            str(requirement.get("title", "")),
            str(requirement.get("description", "")),
        ]
    ).lower()
    return any(keyword in haystack for keyword in EXPERIENCE_TRIGGER_KEYWORDS)


def _ensure_json_store(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]")


def load_pm_clarification_store(path: Path) -> list[dict[str, object]]:
    _ensure_json_store(path)
    try:
        raw_items = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []
    return [item for item in raw_items if isinstance(item, dict)]


def save_pm_clarification_store(path: Path, items: list[dict[str, object]]) -> None:
    _ensure_json_store(path)
    path.write_text(json.dumps(items, indent=2))


def create_pm_clarification(
    path: Path,
    *,
    project_name: str,
    requirement_id: str,
    requirement_title: str,
    source_thread_id: str = "",
    summary: str,
    questions: list[str],
) -> dict[str, object]:
    items = load_pm_clarification_store(path)
    clarification = {
        "clarification_id": str(uuid4()),
        "project_name": project_name.strip(),
        "requirement_id": requirement_id.strip(),
        "requirement_title": requirement_title.strip(),
        "source_thread_id": source_thread_id.strip(),
        "summary": summary.strip(),
        "questions": [question.strip() for question in questions if question.strip()],
        "status": "OPEN",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": "",
    }
    items.append(clarification)
    save_pm_clarification_store(path, items)
    return clarification


def resolve_pm_clarification_in_store(path: Path, clarification_id: str) -> dict[str, object]:
    items = load_pm_clarification_store(path)
    matching = next((item for item in items if str(item.get("clarification_id")) == clarification_id), None)
    if matching is None:
        raise ValueError(f"PM clarification not found: {clarification_id}")
    matching["status"] = "RESOLVED"
    matching["resolved_at"] = datetime.now(timezone.utc).isoformat()
    save_pm_clarification_store(path, items)
    return matching
