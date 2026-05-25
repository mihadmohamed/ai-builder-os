from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import json
import errno
import mimetypes
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parents[3]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

from create_project import scaffold_project  # type: ignore  # noqa: E402
from qa_report import (  # type: ignore  # noqa: E402
    parse_report as parse_qa_report,
    reliability_statement as qa_reliability_statement,
    resolve_runner as resolve_qa_runner,
    run_runner as run_qa_runner,
)
from tools.common import (  # noqa: E402
    active_agent_threads as load_active_agent_threads,
    active_experience_findings as load_active_experience_findings,
    active_pm_clarifications as load_active_pm_clarifications,
    create_pm_clarification,
    iter_projects,
    load_pm_clarification_store,
    parse_requirements,
    parse_tasks,
    requirement_has_experience_trigger,
    requirement_has_structural_trigger,
    requirement_has_ui_trigger,
    resolve_pm_clarification_in_store,
    save_pm_clarification_store,
    validate_project_structure,
)


REQUIREMENT_BLOCK_PATTERN = re.compile(
    r"###\s+(R\d+)\s+—\s+(.+?)\n\n"
    r"Status:\s+(.+?)\n"
    r"(?:Priority:\s+(.+?)\n)?"
    r"(?:Effort:\s+(.+?)\n)?"
    r"Description:\n"
    r"(.*?)(?=\n###\s+R\d+\s+—|\n---|\Z)",
    re.DOTALL,
)
TASK_BLOCK_PATTERN = re.compile(
    r"^##\s+Task\s+(\d+):\s+(.+?)\n\n"
    r"Type:\s+(.+?)\n"
    r"Status:\s+(.+?)\n"
    r"Requirement(?:s)?:\s+(.+?)\n\n"
    r"(.*?)(?=^##\s+Task\s+\d+:|\Z)",
    re.DOTALL | re.MULTILINE,
)

ACTIVE_HEADER = "## Active Requirements"
BACKLOG_HEADER = "## Backlog (Not yet prioritised)"
RULES_HEADER = "## Rules"
REQUIREMENT_RULES_HEADER = "## Requirement Rules"
PRODUCT_REQUIREMENTS_HEADER = "# Product Requirements"
EXPERIENCE_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "experience_findings.json"
IMPLEMENTATION_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "implementation_runs.json"
AGENT_THREAD_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "agent_threads.json"
APPROVAL_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "approvals.json"
SPRINT_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "sprint.json"
QUALITY_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "quality_reviews.json"
MANUAL_VERIFICATION_FILE = REPO_ROOT / "projects" / "os-control-panel" / "data" / "manual_verifications.json"
AGENT_UPLOAD_DIR = REPO_ROOT / "projects" / "os-control-panel" / "data" / "agent_uploads"
IMPLEMENTATION_LOG_DIR = REPO_ROOT / "projects" / "os-control-panel" / "data" / "implementation_logs"
IMPLEMENTATION_ACTIVE_STATES = {"QUEUED", "RUNNING"}
SPRINT_ACTIVE_STATES = {"PLANNING", "ACTIVE", "BLOCKED", "READY_TO_CLOSE"}
IMPLEMENTATION_STALE_MINUTES = 5
PREVIEW_PORT_BASE = 8600
PREVIEW_PORT_SPAN = 300
EXPERIENCE_HANDOFF_STATES = {
    "ready_for_pm_review",
    "ready_for_product_director",
    "handoff_prepared",
    "routed",
    "accepted",
    "resolved",
    "superseded",
}


@dataclass(frozen=True)
class RequirementSummary:
    id: str
    title: str
    status: str


@dataclass(frozen=True)
class TaskSummary:
    id: str
    title: str
    status: str


@dataclass(frozen=True)
class RequirementRecord:
    id: str
    title: str
    status: str
    priority: str
    effort: str
    description: str


@dataclass(frozen=True)
class RequirementDocument:
    intro: str
    active_requirements: tuple[RequirementRecord, ...]
    backlog_requirements: tuple[RequirementRecord, ...]
    rules_text: str


@dataclass(frozen=True)
class TaskBlock:
    number: int
    title: str
    task_type: str
    status: str
    requirements: tuple[str, ...]
    body: str


@dataclass(frozen=True)
class TaskDocument:
    intro: str
    tasks: tuple[TaskBlock, ...]


@dataclass(frozen=True)
class ProjectSummary:
    name: str
    path: Path
    structure_ok: bool
    missing_paths: tuple[str, ...]
    requirement_counts: dict[str, int]
    new_requirements: tuple[RequirementSummary, ...]
    task_counts: dict[str, int]
    pending_tasks: tuple[TaskSummary, ...]


@dataclass(frozen=True)
class RequirementRecommendation:
    requirement_id: str
    title: str
    rationale: str


@dataclass(frozen=True)
class DiscoveryQuestion:
    id: str
    prompt: str


@dataclass(frozen=True)
class DiscoveryPlan:
    mode: str
    framing: str
    questions: tuple[DiscoveryQuestion, ...]


@dataclass(frozen=True)
class AgentMessage:
    role: str
    content: str
    created_at: str
    attachments: tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentThread:
    thread_id: str
    project_name: str
    agent_name: str
    mode: str
    status: str
    idea: str
    planner_type: str
    plan_mode: str
    current_question_index: int
    current_field_id: str
    answers: dict[str, str]
    draft_title: str
    draft: str
    draft_data: dict[str, str]
    messages: tuple[AgentMessage, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ExperienceFinding:
    finding_id: str
    project_name: str
    user_problem: str
    affected_workflow: str
    evidence: str
    confidence: str
    severity: str
    frequency: str
    recommendation_type: str
    rationale: str
    recommended_next_role: str
    handoff_state: str
    created_at: str


@dataclass(frozen=True)
class ExperienceIntakePlan:
    affected_workflow_prompt: str
    evidence_prompt: str
    rationale_prompt: str
    recommendation_type: str


@dataclass(frozen=True)
class ImplementationRun:
    run_id: str
    project_name: str
    requirement_id: str
    requirement_title: str
    status: str
    summary: str
    error: str
    created_at: str
    started_at: str
    finished_at: str
    output_path: str
    log_path: str
    worker_pid: int | None


@dataclass(frozen=True)
class ImplementationRunInspection:
    run: ImplementationRun
    display_status: str
    tone: Literal["active", "completed", "failed", "stale"]
    output_available: bool
    log_available: bool
    output_excerpt: str
    log_excerpt: str


@dataclass(frozen=True)
class ProjectPreview:
    project_name: str
    available: bool
    runtime: str
    entry_path: Path | None
    url: str
    command: tuple[str, ...]
    status_text: str


@dataclass(frozen=True)
class SprintPlan:
    project_name: str
    status: str
    requirement_ids: tuple[str, ...]
    created_at: str
    started_at: str
    completed_at: str
    current_requirement_id: str
    blocked_reason: str


IMPLEMENTATION_PROGRESS_BY_STATUS = {
    "QUEUED": 10,
    "RUNNING": 55,
    "COMPLETED": 100,
    "FAILED": 100,
}

IMPLEMENTATION_PROGRESS_MESSAGE_BY_STATUS = {
    "QUEUED": "Implementation is queued and waiting for the background worker to start.",
    "RUNNING": "Implementation is running; Codex is working through the OS workflow.",
    "COMPLETED": "Implementation finished; review the summary below.",
    "FAILED": "Implementation stopped with an error; review the error below.",
}

IMPLEMENTATION_STALE_ERROR_FRAGMENT = "marked failed during reconciliation"


@dataclass(frozen=True)
class PMClarification:
    clarification_id: str
    project_name: str
    requirement_id: str
    requirement_title: str
    source_thread_id: str
    summary: str
    questions: tuple[str, ...]
    status: str
    created_at: str
    resolved_at: str


@dataclass(frozen=True)
class RequirementDeletionResult:
    deleted_requirement: RequirementRecord
    removed_tasks: int
    updated_tasks: int
    removed_clarifications: int
    removed_implementation_runs: int


@dataclass(frozen=True)
class OrchestratorRecommendation:
    next_action: str
    next_role: str
    why: str


@dataclass(frozen=True)
class ArchitectReviewSnapshot:
    headline: str
    summary: str
    hotspots: tuple[str, ...]
    guardrails: tuple[str, ...]


@dataclass(frozen=True)
class QAReviewSnapshot:
    runner_path: str
    summary: str
    failures: tuple[str, ...]
    confidence: str
    raw_output: str


@dataclass(frozen=True)
class QualityReviewRecord:
    review_id: str
    project_name: str
    mode: str
    status: str
    runner_path: str
    summary: str
    failures: tuple[str, ...]
    confidence: str
    raw_output: str
    reviewed_at: str


@dataclass(frozen=True)
class ManualVerificationCheck:
    check_id: str
    title: str
    instructions: str
    status: str
    notes: str
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ManualVerificationPlan:
    project_name: str
    requirement_id: str
    checks: tuple[ManualVerificationCheck, ...]
    created_at: str
    updated_at: str


@dataclass(frozen=True)
class ManualVerificationSummary:
    requirement_id: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    not_run_checks: int
    signoff_state: str
    signoff_label: str


@dataclass(frozen=True)
class ApprovalRequest:
    approval_id: str
    project_name: str
    approval_type: str
    source_thread_id: str
    source_agent_name: str
    title: str
    summary: str
    payload: dict[str, str]
    status: str
    created_at: str
    resolved_at: str


@dataclass(frozen=True)
class WorkflowTimelineEvent:
    event_id: str
    project_name: str
    occurred_at: str
    title: str
    summary: str
    actor: str
    artifact_kind: str
    artifact_id: str
    status_bucket: str
    detail: str


@dataclass(frozen=True)
class InboxItem:
    kind: str
    title: str
    summary: str
    project_name: str
    status_bucket: str
    reference_id: str
    detail: str


@dataclass(frozen=True)
class AgentSummary:
    name: str
    title: str
    can_do: tuple[str, ...]
    memory_context: tuple[str, ...]
    workflow_position: tuple[str, ...]


@dataclass(frozen=True)
class LivePMProjectThread:
    thread_id: str
    project_name: str
    display_name: str
    planner_type: str
    status: str
    messages: tuple[AgentMessage, ...]
    draft_title: str
    draft_requirement: str
    created_at: str
    updated_at: str


class LivePMTurn(BaseModel):
    next_action: Literal["ask_question", "draft_requirements", "request_clarification"]
    assistant_message: str
    draft_title: str = ""
    draft_requirement: str = ""
    clarification_summary: str = ""
    clarification_questions: list[str] = []


class LivePMDiscoveryError(RuntimeError):
    pass


class LiveExperienceTurn(BaseModel):
    next_action: Literal["ask_question", "draft_finding"]
    assistant_message: str
    finding_draft: str = ""
    user_problem: str = ""
    affected_workflow: str = ""
    evidence: str = ""
    confidence: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    severity: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    frequency: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    recommendation_type: Literal["UX improvement in scope", "feature candidate", "scope escalation"] = "UX improvement in scope"
    rationale: str = ""


class LiveUIDesignTurn(BaseModel):
    next_action: Literal["ask_question", "draft_design_brief"]
    assistant_message: str
    draft_title: str = ""
    design_brief: str = ""


class LivePMReviewCompletionTurn(BaseModel):
    next_action: Literal["create_backlog_requirement", "confirm_out_of_scope"]
    assistant_message: str
    requirement_title: str = ""
    requirement_body: str = ""
    priority: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    effort: Literal["S", "M", "L"] = "M"
    scope_confirmation_title: str = ""
    scope_confirmation_summary: str = ""


REQUIREMENT_CONSOLIDATION_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "that",
    "this",
    "will",
    "have",
    "has",
    "are",
    "but",
    "not",
    "than",
    "then",
    "when",
    "where",
    "what",
    "which",
    "your",
    "their",
    "there",
    "about",
    "after",
    "before",
    "under",
    "while",
    "more",
    "less",
    "very",
    "over",
    "only",
    "just",
    "make",
    "need",
    "needs",
    "improve",
    "improved",
    "improvement",
    "enhance",
    "enhanced",
    "launch",
    "introduce",
    "broader",
    "initiative",
    "project",
    "product",
    "design",
    "review",
}


ROLE_CARDS = (
    {
        "name": "PM",
        "title": "Tom",
        "summary": "Clarifies ideas, drafts requirements, and turns approved work into structured tasks.",
    },
    {
        "name": "Experience Designer",
        "title": "Enzo",
        "summary": "Synthesises UX feedback into structured findings and routes them into the OS without taking over PM or engineering work.",
    },
    {
        "name": "UI Designer",
        "title": "Ricky",
        "summary": "Shapes visual direction, interaction design, layout decisions, and interface polish before and after implementation.",
    },
    {
        "name": "Architect",
        "title": "Andy",
        "summary": "Reviews structure, workflow design, and maintainability when the shape of the system is the real problem.",
    },
    {
        "name": "Orchestrator",
        "title": "Paul",
        "summary": "Inspects project state and recommends which role should run next without executing the work directly.",
    },
    {
        "name": "Engineer",
        "title": "Maciej",
        "summary": "Implements tasks, preserves behavior, and validates technical changes before closing work.",
    },
    {
        "name": "QA",
        "title": "Richard",
        "summary": "Runs validation, checks regressions, and flags obvious UX clarity issues on user-facing changes.",
    },
)

AGENT_SUMMARY_OVERRIDES: dict[str, dict[str, tuple[str, ...]]] = {
    "PM": {
        "can_do": (
            "Clarify ideas and turn them into structured requirements.",
            "Prioritise real `NEW` work before execution begins.",
            "Translate approved requirements into concrete, testable tasks.",
        ),
        "memory_context": (
            "Interrogate ambiguity before tasking downstream work.",
            "Prefer small, testable tasks over broad implementation asks.",
            "Keep PM focused on product definition rather than code changes.",
        ),
        "workflow_position": (
            "Usually the first formal OS role after an idea or approved finding enters the workflow.",
            "Runs after Experience Designer when raw UX feedback needs synthesis first.",
            "Hands structured tasks to downstream implementation once scope is clear.",
        ),
    },
    "Experience Designer": {
        "can_do": (
            "Gather and interpret user experience feedback.",
            "Synthesize usability issues and workflow friction into structured findings.",
            "Review an existing surface for clarity, hierarchy, scanability, and interaction quality.",
        ),
        "memory_context": (
            "Separate evidence from assumptions before suggesting product action.",
            "Keep findings inside current scope unless escalation is clearly justified.",
            "Route product work through PM or Product Director instead of implementing directly.",
        ),
        "workflow_position": (
            "Runs before PM when the main input is raw UX feedback, workflow friction, or user pain.",
            "Can also review a live surface before or after implementation when usability is the real question.",
            "Hands a structured finding into the workflow rather than taking over prioritisation or engineering.",
        ),
    },
    "UI Designer": {
        "can_do": (
            "Propose visual and interaction direction for user-facing surfaces.",
            "Shape layout, hierarchy, flow, and interface decisions before implementation settles.",
            "Review existing UI work and identify improvements in polish, consistency, or clarity.",
        ),
        "memory_context": (
            "Ground design recommendations in the actual workflow, not taste alone.",
            "Keep interface guidance implementable, concrete, and scoped.",
            "Route tracked design work through PM when it should become product work.",
        ),
        "workflow_position": (
            "Runs when interface direction, layout, interaction design, or visual polish is the real issue.",
            "Often shapes work before implementation, but can also critique a surface that already exists.",
            "Collaborates with PM and Experience Designer instead of bypassing the normal workflow.",
        ),
    },
    "Architect": {
        "can_do": (
            "Review system structure, role boundaries, validation design, and documentation shape.",
            "Identify structural risks, inconsistencies, and scaling problems.",
            "Recommend small, coherent changes that improve clarity and maintainability.",
        ),
        "memory_context": (
            "Start with diagnosis before proposing change.",
            "Prefer evolutionary improvements over grand redesigns.",
            "Keep guidance concrete and sequenceable so Engineer can act on it safely.",
        ),
        "workflow_position": (
            "Runs before Engineer when planned work introduces meaningful structural change.",
            "Helps when the shape of the system or workflow is the real problem.",
            "Narrows the implementation path before more engineering pressure is added.",
        ),
    },
    "Orchestrator": {
        "can_do": (
            "Inspect current project state and decide which role should run next.",
            "Route workflow based on requirements, tasks, and active workflow artifacts.",
            "Surface blocking clarifications, approvals, or handoffs before downstream work continues.",
        ),
        "memory_context": (
            "Route based on current file state rather than prior conversation context.",
            "Treat routed findings and clarifications as real workflow state when the project uses them.",
            "Recommend the simplest valid next step without doing the work yourself.",
        ),
        "workflow_position": (
            "Runs when the main question is what should happen next in the workflow.",
            "Can sit between any two roles as a routing layer, especially before engineering or QA.",
            "Keeps workflow movement inspectable without taking over PM, Engineer, or QA work directly.",
        ),
    },
    "Engineer": {
        "can_do": (
            "Implement approved tasks from `product/tasks.md`.",
            "Preserve behavior while changing code, prompts, or validation logic.",
            "Build the smallest viable implementation or validation mechanism needed next.",
        ),
        "memory_context": (
            "Proceed directly when the task is clear, but stop when requirements conflict or drift.",
            "Prefer simple, maintainable solutions over brittle or over-engineered ones.",
            "Move tasks to `DONE` only after successful validation.",
        ),
        "workflow_position": (
            "Runs after PM has created tasks and after Architect when structural triggers apply.",
            "Moves approved work through implementation and technical validation.",
            "Hands meaningful changes to QA rather than declaring the work complete on its own.",
        ),
    },
    "QA": {
        "can_do": (
            "Run the project validation path and summarize pass or fail status.",
            "Check regressions and mismatches against expected behavior.",
            "Flag obvious clarity issues on user-facing changes without redesigning the interface.",
        ),
        "memory_context": (
            "Treat eval and test results as the source of truth for validation work.",
            "Keep reporting precise, objective, and scoped to observed behavior.",
            "Report broken validation paths as system issues instead of papering over them.",
        ),
        "workflow_position": (
            "Usually runs after meaningful implementation changes.",
            "Confirms whether the system still behaves correctly before work is treated as done.",
            "Loops failures back into implementation or workflow review instead of changing code directly.",
        ),
    },
}


def list_agent_summaries() -> tuple[AgentSummary, ...]:
    return tuple(_build_agent_summary(role) for role in ROLE_CARDS)


def agent_summary_by_name(name: str) -> AgentSummary:
    for summary in list_agent_summaries():
        if summary.name == name:
            return summary
    raise ValueError(f"Agent summary not found: {name}")


def _requirements_path(project_name: str) -> Path:
    return REPO_ROOT / "projects" / project_name / "product" / "requirements.md"


def _role_doc_path(role_name: str) -> Path:
    file_map = {
        "PM": "pm.md",
        "Experience Designer": "experience-designer.md",
        "UI Designer": "ui-designer.md",
        "Engineer": "engineer.md",
        "QA": "qa.md",
        "Architect": "architect.md",
        "Orchestrator": "orchestrator.md",
    }
    return REPO_ROOT / "agent" / "roles" / file_map[role_name]


def architect_review_snapshot(project_name: str) -> ArchitectReviewSnapshot:
    project_dir = REPO_ROOT / "projects" / project_name
    requirements = parse_requirements(project_dir / "product" / "requirements.md")
    tasks = parse_tasks(project_dir / "product" / "tasks.md")
    approvals = active_approvals(project_name)
    clarifications = active_pm_clarifications(project_name)
    sprint = load_sprint_plan(project_name)
    active_run = active_implementation_run(project_name)

    requirement_by_id = {item["id"]: item for item in requirements}
    hotspots: list[str] = []
    for task in tasks:
        if task["status"] not in {"TODO", "IN_PROGRESS"}:
            continue
        linked = [requirement_by_id[req_id] for req_id in task.get("requirements", []) if req_id in requirement_by_id]
        if any(requirement_has_structural_trigger(item) for item in linked):
            linked_ids = ", ".join(item["id"] for item in linked) or "linked requirement"
            hotspots.append(f"{task['id']} is pending with structural triggers on {linked_ids}.")

    if approvals:
        hotspots.append(f"{len(approvals)} open approval item(s) are still part of active workflow state.")
    if clarifications:
        hotspots.append(f"{len(clarifications)} open PM clarification(s) still block downstream work.")
    if sprint is not None and sprint.status == "BLOCKED":
        hotspots.append(f"Sprint is blocked on {sprint.current_requirement_id or 'the current requirement'}.")
    if active_run is not None:
        hotspots.append(f"Implementation run {active_run.run_id} is currently {active_run.status} for {active_run.requirement_id}.")

    if hotspots:
        headline = "Architect attention is warranted."
        summary = "The project has active structural or workflow-shaping conditions that should be reviewed before more implementation pressure is added."
    else:
        headline = "No active structural hotspot detected."
        summary = "The current project state does not show an immediate architecture trigger, though broader cleanup and consolidation decisions may still be valuable."

    guardrails = (
        "Prefer evolutionary fixes over broad redesign.",
        "Keep workflow state, product state, and runtime state clearly separated.",
        "Narrow broad UI or workflow initiatives before they become overlapping backlog items.",
    )
    return ArchitectReviewSnapshot(
        headline=headline,
        summary=summary,
        hotspots=tuple(hotspots),
        guardrails=guardrails,
    )


def run_project_qa_review(project_name: str, mode: str = "deterministic") -> QAReviewSnapshot:
    runner_path = resolve_qa_runner(project_name, mode)
    if runner_path is None:
        return QAReviewSnapshot(
            runner_path="",
            summary="No validation runner is available for this project and mode.",
            failures=(),
            confidence="Low confidence: no validation path is available.",
            raw_output="",
        )

    completed = run_qa_runner(runner_path)
    combined_output = completed.stdout.strip()
    if completed.stderr.strip():
        combined_output = f"{combined_output}\n{completed.stderr.strip()}".strip()
    summary, failures = parse_qa_report(combined_output)
    if summary is None:
        summary_text = "FAIL: no parseable pass/fail summary was found."
    else:
        passed, total = summary
        status = "PASS" if completed.returncode == 0 else "FAIL"
        summary_text = f"{status}: {passed}/{total} passing ({mode})"
    confidence = qa_reliability_statement(summary, completed.returncode)
    return QAReviewSnapshot(
        runner_path=str(runner_path.relative_to(REPO_ROOT)),
        summary=summary_text,
        failures=tuple(failures),
        confidence=confidence,
        raw_output=combined_output,
    )


def _load_quality_reviews() -> list[dict[str, object]]:
    if not QUALITY_FILE.exists():
        return []
    try:
        payload = json.loads(QUALITY_FILE.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _save_quality_reviews(items: list[dict[str, object]]) -> None:
    QUALITY_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_FILE.write_text(json.dumps(items, indent=2))


def _quality_review_from_dict(raw_item: dict[str, object]) -> QualityReviewRecord:
    failures = raw_item.get("failures", [])
    if not isinstance(failures, list):
        failures = []
    return QualityReviewRecord(
        review_id=str(raw_item.get("review_id", "")),
        project_name=str(raw_item.get("project_name", "")),
        mode=str(raw_item.get("mode", "deterministic")),
        status=str(raw_item.get("status", "")),
        runner_path=str(raw_item.get("runner_path", "")),
        summary=str(raw_item.get("summary", "")),
        failures=tuple(str(item) for item in failures),
        confidence=str(raw_item.get("confidence", "")),
        raw_output=str(raw_item.get("raw_output", "")),
        reviewed_at=str(raw_item.get("reviewed_at", "")),
    )


def list_quality_reviews(project_name: str, *, mode: str | None = None) -> list[QualityReviewRecord]:
    items = [item for item in _load_quality_reviews() if str(item.get("project_name", "")) == project_name]
    if mode is not None:
        items = [item for item in items if str(item.get("mode", "")) == mode]
    return [
        _quality_review_from_dict(item)
        for item in sorted(items, key=lambda candidate: str(candidate.get("reviewed_at", "")), reverse=True)
    ]


def latest_quality_review(project_name: str, *, mode: str = "deterministic") -> QualityReviewRecord | None:
    reviews = list_quality_reviews(project_name, mode=mode)
    return reviews[0] if reviews else None


def record_project_qa_review(project_name: str, mode: str = "deterministic") -> QualityReviewRecord:
    snapshot = run_project_qa_review(project_name, mode=mode)
    status = "PASS" if snapshot.summary.startswith("PASS:") else "FAIL"
    review = {
        "review_id": str(uuid4()),
        "project_name": project_name,
        "mode": mode,
        "status": status,
        "runner_path": snapshot.runner_path,
        "summary": snapshot.summary,
        "failures": list(snapshot.failures),
        "confidence": snapshot.confidence,
        "raw_output": snapshot.raw_output,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    items = _load_quality_reviews()
    items.append(review)
    _save_quality_reviews(items)
    return _quality_review_from_dict(review)


def _load_manual_verifications() -> list[dict[str, object]]:
    if not MANUAL_VERIFICATION_FILE.exists():
        return []
    try:
        payload = json.loads(MANUAL_VERIFICATION_FILE.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _save_manual_verifications(items: list[dict[str, object]]) -> None:
    MANUAL_VERIFICATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    MANUAL_VERIFICATION_FILE.write_text(json.dumps(items, indent=2))


def _manual_verification_check_from_dict(raw_item: dict[str, object]) -> ManualVerificationCheck:
    return ManualVerificationCheck(
        check_id=str(raw_item.get("check_id", "")),
        title=str(raw_item.get("title", "")),
        instructions=str(raw_item.get("instructions", "")),
        status=str(raw_item.get("status", "NOT_RUN")),
        notes=str(raw_item.get("notes", "")),
        created_at=str(raw_item.get("created_at", "")),
        updated_at=str(raw_item.get("updated_at", "")),
    )


def _manual_verification_plan_from_dict(raw_item: dict[str, object]) -> ManualVerificationPlan:
    raw_checks = raw_item.get("checks", [])
    checks = tuple(
        _manual_verification_check_from_dict(check)
        for check in raw_checks
        if isinstance(check, dict)
    )
    return ManualVerificationPlan(
        project_name=str(raw_item.get("project_name", "")),
        requirement_id=str(raw_item.get("requirement_id", "")),
        checks=checks,
        created_at=str(raw_item.get("created_at", "")),
        updated_at=str(raw_item.get("updated_at", "")),
    )


def manual_verification_plan(project_name: str, requirement_id: str) -> ManualVerificationPlan | None:
    matching = next(
        (
            item
            for item in _load_manual_verifications()
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    if matching is None:
        return None
    return _manual_verification_plan_from_dict(matching)


def _signoff_state_for_counts(total_checks: int, passed_checks: int, failed_checks: int, not_run_checks: int) -> tuple[str, str]:
    if total_checks == 0:
        return ("NO_PLAN", "No verification plan")
    if failed_checks > 0:
        return ("BLOCKED", "Blocked by failing checks")
    if passed_checks == total_checks:
        return ("READY_FOR_SIGNOFF", "Ready for signoff")
    if not_run_checks == total_checks:
        return ("NOT_STARTED", "Verification not started")
    return ("IN_PROGRESS", "Verification in progress")


def manual_verification_summary(project_name: str, requirement_id: str) -> ManualVerificationSummary:
    plan = manual_verification_plan(project_name, requirement_id)
    checks = plan.checks if plan is not None else ()
    total_checks = len(checks)
    passed_checks = sum(1 for check in checks if check.status == "PASS")
    failed_checks = sum(1 for check in checks if check.status == "FAIL")
    not_run_checks = sum(1 for check in checks if check.status == "NOT_RUN")
    signoff_state, signoff_label = _signoff_state_for_counts(
        total_checks,
        passed_checks,
        failed_checks,
        not_run_checks,
    )
    return ManualVerificationSummary(
        requirement_id=requirement_id,
        total_checks=total_checks,
        passed_checks=passed_checks,
        failed_checks=failed_checks,
        not_run_checks=not_run_checks,
        signoff_state=signoff_state,
        signoff_label=signoff_label,
    )


def add_manual_verification_check(
    project_name: str,
    requirement_id: str,
    *,
    title: str,
    instructions: str,
) -> ManualVerificationPlan:
    title_text = title.strip()
    if not title_text:
        raise ValueError("Verification check title is required.")

    items = _load_manual_verifications()
    matching = next(
        (
            item
            for item in items
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    now = datetime.now(timezone.utc).isoformat()
    if matching is None:
        matching = {
            "project_name": project_name,
            "requirement_id": requirement_id,
            "checks": [],
            "created_at": now,
            "updated_at": now,
        }
        items.append(matching)

    raw_checks = matching.setdefault("checks", [])
    if not isinstance(raw_checks, list):
        raw_checks = []
        matching["checks"] = raw_checks
    raw_checks.append(
        {
            "check_id": str(uuid4()),
            "title": title_text,
            "instructions": instructions.strip(),
            "status": "NOT_RUN",
            "notes": "",
            "created_at": now,
            "updated_at": now,
        }
    )
    matching["updated_at"] = now
    _save_manual_verifications(items)
    return _manual_verification_plan_from_dict(matching)


def update_manual_verification_check(
    project_name: str,
    requirement_id: str,
    check_id: str,
    *,
    status: str,
    notes: str,
) -> ManualVerificationPlan:
    normalized_status = status.strip().upper()
    if normalized_status not in {"NOT_RUN", "PASS", "FAIL"}:
        raise ValueError(f"Invalid verification status: {status}")

    items = _load_manual_verifications()
    matching = next(
        (
            item
            for item in items
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Manual verification plan not found: {project_name} {requirement_id}")

    raw_checks = matching.get("checks", [])
    if not isinstance(raw_checks, list):
        raise ValueError(f"Manual verification plan is malformed: {project_name} {requirement_id}")
    raw_check = next((check for check in raw_checks if str(check.get("check_id", "")) == check_id), None)
    if raw_check is None:
        raise ValueError(f"Manual verification check not found: {check_id}")

    now = datetime.now(timezone.utc).isoformat()
    raw_check["status"] = normalized_status
    raw_check["notes"] = notes.strip()
    raw_check["updated_at"] = now
    matching["updated_at"] = now
    _save_manual_verifications(items)
    return _manual_verification_plan_from_dict(matching)


def remove_manual_verification_check(project_name: str, requirement_id: str, check_id: str) -> ManualVerificationPlan | None:
    items = _load_manual_verifications()
    matching = next(
        (
            item
            for item in items
            if str(item.get("project_name", "")) == project_name
            and str(item.get("requirement_id", "")) == requirement_id
        ),
        None,
    )
    if matching is None:
        return None

    raw_checks = matching.get("checks", [])
    if not isinstance(raw_checks, list):
        return _manual_verification_plan_from_dict(matching)

    remaining_checks = [check for check in raw_checks if str(check.get("check_id", "")) != check_id]
    if len(remaining_checks) == len(raw_checks):
        return _manual_verification_plan_from_dict(matching)

    if not remaining_checks:
        items = [
            item
            for item in items
            if not (
                str(item.get("project_name", "")) == project_name
                and str(item.get("requirement_id", "")) == requirement_id
            )
        ]
        _save_manual_verifications(items)
        return None

    matching["checks"] = remaining_checks
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_manual_verifications(items)
    return _manual_verification_plan_from_dict(matching)


def _section_lines(path: Path, heading: str) -> list[str]:
    lines = path.read_text().splitlines()
    target = heading.strip().lower()
    start_index: int | None = None
    start_level = 0
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        hashes = len(stripped) - len(stripped.lstrip("#"))
        title = stripped[hashes:].strip().lower()
        if title == target:
            start_index = index + 1
            start_level = hashes
            break
    if start_index is None:
        return []

    collected: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            if hashes <= start_level:
                break
        collected.append(line.rstrip())
    return collected


def _extract_bullets(lines: list[str]) -> tuple[str, ...]:
    bullets: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(("* ", "- ")):
            bullets.append(stripped[2:].strip())
    return tuple(bullets)


def _workflow_position_bullets(role_name: str) -> tuple[str, ...]:
    workflow_path = REPO_ROOT / "agent" / "workflow.md"
    lines = workflow_path.read_text().splitlines()
    start_pattern = f"{role_name.lower()} agent"
    start_index: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip().lower()
        if stripped[:1].isdigit() and start_pattern in stripped:
            start_index = index + 1
            break
    if start_index is None:
        return ()

    collected: list[str] = []
    for line in lines[start_index:]:
        stripped = line.strip()
        lowered = stripped.lower()
        if lowered[:1].isdigit() and lowered.endswith("agent") and "." in lowered:
            break
        collected.append(line.rstrip())
    return _extract_bullets(collected)


def _agent_memory_context(role_name: str) -> tuple[str, ...]:
    role_path = _role_doc_path(role_name)
    sections = ["Rules", "Behaviour Rules", "Memory Enforcement Rule"]
    bullets: list[str] = []
    for section in sections:
        bullets.extend(_extract_bullets(_section_lines(role_path, section)))
    seen: set[str] = set()
    deduped: list[str] = []
    for bullet in bullets:
        if bullet in seen:
            continue
        seen.add(bullet)
        deduped.append(bullet)
    return tuple(deduped[:3])


def _agent_can_do(role_name: str) -> tuple[str, ...]:
    role_path = _role_doc_path(role_name)
    bullets = _extract_bullets(_section_lines(role_path, "Responsibilities"))
    filtered = tuple(bullet for bullet in bullets if not bullet.startswith("Read "))
    return filtered[:3] or bullets[:3]


def _build_agent_summary(role: dict[str, str]) -> AgentSummary:
    name = role["name"]
    overrides = AGENT_SUMMARY_OVERRIDES.get(name, {})
    return AgentSummary(
        name=name,
        title=role["title"],
        can_do=overrides.get("can_do", _agent_can_do(name)),
        memory_context=overrides.get("memory_context", _agent_memory_context(name)),
        workflow_position=overrides.get("workflow_position", _workflow_position_bullets(name)),
    )


def _tasks_path(project_name: str) -> Path:
    return REPO_ROOT / "projects" / project_name / "product" / "tasks.md"


def _pm_clarifications_path(project_name: str) -> Path:
    return REPO_ROOT / "projects" / project_name / "data" / "pm_clarifications.json"


def _ensure_agent_thread_store() -> None:
    AGENT_THREAD_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not AGENT_THREAD_FILE.exists():
        AGENT_THREAD_FILE.write_text("[]")


def _ensure_experience_store() -> None:
    EXPERIENCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not EXPERIENCE_FILE.exists():
        EXPERIENCE_FILE.write_text("[]")


def _ensure_implementation_store() -> None:
    IMPLEMENTATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    IMPLEMENTATION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not IMPLEMENTATION_FILE.exists():
        IMPLEMENTATION_FILE.write_text("[]")


def _ensure_approval_store() -> None:
    APPROVAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not APPROVAL_FILE.exists():
        APPROVAL_FILE.write_text("[]")


def _ensure_pm_clarification_store(project_name: str) -> None:
    path = _pm_clarifications_path(project_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]")


def _normalize_priority(value: str) -> str:
    value = value.strip()
    return value.upper() if value else ""


def _normalize_effort(value: str) -> str:
    value = value.strip()
    return value.upper() if value else ""


def _parse_requirement_section(section_text: str) -> tuple[RequirementRecord, ...]:
    records: list[RequirementRecord] = []
    for match in REQUIREMENT_BLOCK_PATTERN.finditer(section_text.strip()):
        description = match.group(6).strip()
        records.append(
            RequirementRecord(
                id=match.group(1).strip(),
                title=match.group(2).strip(),
                status=match.group(3).strip(),
                priority=_normalize_priority(match.group(4) or ""),
                effort=_normalize_effort(match.group(5) or ""),
                description=description,
            )
        )
    return tuple(records)


def _parse_task_document(text: str) -> TaskDocument:
    matches = list(TASK_BLOCK_PATTERN.finditer(text))
    if not matches:
        return TaskDocument(intro=text.rstrip(), tasks=())

    intro = text[: matches[0].start()].rstrip()
    tasks: list[TaskBlock] = []
    for match in matches:
        tasks.append(
            TaskBlock(
                number=int(match.group(1)),
                title=match.group(2).strip(),
                task_type=match.group(3).strip(),
                status=match.group(4).strip(),
                requirements=tuple(re.findall(r"\bR\d+\b", match.group(5))),
                body=match.group(6).rstrip(),
            )
        )
    return TaskDocument(intro=intro, tasks=tuple(tasks))


def load_task_document(project_name: str) -> TaskDocument:
    path = _tasks_path(project_name)
    text = path.read_text()
    return _parse_task_document(text)


def _render_task_block(task: TaskBlock) -> str:
    requirement_label = "Requirements" if len(task.requirements) != 1 else "Requirement"
    requirements_text = ", ".join(task.requirements)
    parts = [
        f"## Task {task.number}: {task.title}",
        "",
        f"Type: {task.task_type}",
        f"Status: {task.status}",
        f"{requirement_label}: {requirements_text}",
        "",
        task.body.rstrip(),
    ]
    return "\n".join(parts).rstrip()


def save_task_document(project_name: str, document: TaskDocument) -> None:
    rendered_tasks = "\n\n".join(_render_task_block(task) for task in document.tasks)
    rendered = document.intro.rstrip()
    if rendered_tasks:
        rendered = f"{rendered}\n\n{rendered_tasks}\n"
    else:
        rendered = f"{rendered}\n"
    _tasks_path(project_name).write_text(rendered)


def load_requirement_document(project_name: str) -> RequirementDocument:
    path = _requirements_path(project_name)
    text = path.read_text()

    if PRODUCT_REQUIREMENTS_HEADER not in text:
        raise ValueError(f"Requirements file missing {PRODUCT_REQUIREMENTS_HEADER}: {path}")

    intro, product_section = text.split(PRODUCT_REQUIREMENTS_HEADER, 1)
    product_section = product_section.strip()

    rules_header = RULES_HEADER if RULES_HEADER in product_section else REQUIREMENT_RULES_HEADER
    if ACTIVE_HEADER not in product_section or BACKLOG_HEADER not in product_section or rules_header not in product_section:
        raise ValueError(f"Requirements file missing expected sections: {path}")

    _, after_active = product_section.split(ACTIVE_HEADER, 1)
    active_text, after_backlog_header = after_active.split(BACKLOG_HEADER, 1)
    backlog_text, rules_text = after_backlog_header.split(rules_header, 1)

    return RequirementDocument(
        intro=intro.rstrip(),
        active_requirements=_parse_requirement_section(active_text),
        backlog_requirements=_parse_requirement_section(backlog_text),
        rules_text=rules_text.strip(),
    )


def next_requirement_id(project_name: str) -> str:
    document = load_requirement_document(project_name)
    records = list(document.active_requirements + document.backlog_requirements)
    highest = 0
    for record in records:
        highest = max(highest, int(record.id.removeprefix("R")))
    return f"R{highest + 1}"


def _render_requirement_block(record: RequirementRecord) -> str:
    lines = [
        f"### {record.id} — {record.title}",
        "",
        f"Status: {record.status}",
    ]
    if record.priority:
        lines.append(f"Priority: {record.priority}")
    if record.effort:
        lines.append(f"Effort: {record.effort}")
    lines.extend(
        [
            "Description:",
            record.description.strip(),
        ]
    )
    return "\n".join(lines).rstrip()


def save_requirement_document(project_name: str, records: list[RequirementRecord], template: RequirementDocument) -> None:
    active_records = [record for record in records if record.status != "BACKLOG"]
    backlog_records = [record for record in records if record.status == "BACKLOG"]

    active_text = "\n\n".join(_render_requirement_block(record) for record in active_records) or "Add active requirements here."
    backlog_text = "\n\n".join(_render_requirement_block(record) for record in backlog_records) or "Add backlog requirements here when needed."

    rendered = "\n".join(
        [
            template.intro.rstrip(),
            "",
            PRODUCT_REQUIREMENTS_HEADER,
            "",
            ACTIVE_HEADER,
            "",
            active_text,
            "",
            "---",
            "",
            BACKLOG_HEADER,
            "",
            backlog_text,
            "",
            "---",
            "",
            RULES_HEADER,
            "",
            template.rules_text.strip(),
            "",
        ]
    )
    _requirements_path(project_name).write_text(rendered)


def recommend_requirement(records: list[RequirementRecord]) -> RequirementRecommendation | None:
    in_progress = [record for record in records if record.status == "IN_PROGRESS"]
    if in_progress:
        selected = in_progress[0]
        return RequirementRecommendation(
            requirement_id=selected.id,
            title=selected.title,
            rationale="Keep the currently active requirement moving before starting additional work.",
        )

    new_records = [record for record in records if record.status == "NEW"]
    if not new_records:
        return None

    priority_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "": 3}
    effort_rank = {"S": 0, "M": 1, "L": 2, "": 3}
    selected = sorted(
        new_records,
        key=lambda record: (
            priority_rank.get(record.priority, 3),
            effort_rank.get(record.effort, 3),
            record.id,
        ),
    )[0]
    return RequirementRecommendation(
        requirement_id=selected.id,
        title=selected.title,
        rationale="Prefer the highest-priority pending requirement, breaking ties toward lower effort.",
    )


def update_requirement(project_name: str, updated_record: RequirementRecord) -> None:
    document = load_requirement_document(project_name)
    all_records = list(document.active_requirements + document.backlog_requirements)
    replaced = False
    new_records: list[RequirementRecord] = []
    for record in all_records:
        if record.id == updated_record.id:
            new_records.append(updated_record)
            replaced = True
        else:
            new_records.append(record)
    if not replaced:
        raise ValueError(f"Requirement not found: {updated_record.id}")
    save_requirement_document(project_name, new_records, document)


def delete_requirement(project_name: str, requirement_id: str) -> RequirementDeletionResult:
    document = load_requirement_document(project_name)
    all_records = list(document.active_requirements + document.backlog_requirements)
    matching = next((record for record in all_records if record.id == requirement_id), None)
    if matching is None:
        raise ValueError(f"Requirement not found: {requirement_id}")
    if matching.status == "DONE":
        raise ValueError(f"Completed requirements cannot be deleted: {requirement_id}")
    active_run = active_implementation_run(project_name)
    if active_run is not None and active_run.requirement_id == requirement_id:
        raise ValueError(f"Requirement cannot be deleted while implementation is active: {requirement_id}")

    remaining_records = [record for record in all_records if record.id != requirement_id]
    save_requirement_document(project_name, remaining_records, document)
    existing_sprint = load_sprint_plan(project_name)
    if existing_sprint is not None and requirement_id in existing_sprint.requirement_ids:
        updated_ids = tuple(item for item in existing_sprint.requirement_ids if item != requirement_id)
        if updated_ids:
            _replace_sprint_plan(
                project_name,
                status="PLANNING" if existing_sprint.status == "PLANNING" else existing_sprint.status,
                requirement_ids=updated_ids,
                created_at=existing_sprint.created_at,
                started_at=existing_sprint.started_at,
                completed_at=existing_sprint.completed_at,
                current_requirement_id="" if existing_sprint.current_requirement_id == requirement_id else existing_sprint.current_requirement_id,
                blocked_reason=existing_sprint.blocked_reason if existing_sprint.current_requirement_id != requirement_id else "",
            )
        else:
            _save_sprint_plan_raw(project_name, None)

    task_document = load_task_document(project_name)
    remaining_tasks: list[TaskBlock] = []
    removed_tasks = 0
    updated_tasks = 0
    for task in task_document.tasks:
        if requirement_id not in task.requirements:
            remaining_tasks.append(task)
            continue

        remaining_requirements = tuple(req for req in task.requirements if req != requirement_id)
        if not remaining_requirements:
            removed_tasks += 1
            continue

        updated_tasks += 1
        remaining_tasks.append(
            TaskBlock(
                number=task.number,
                title=task.title,
                task_type=task.task_type,
                status=task.status,
                requirements=remaining_requirements,
                body=task.body,
            )
        )

    save_task_document(project_name, TaskDocument(intro=task_document.intro, tasks=tuple(remaining_tasks)))

    clarifications = _load_pm_clarifications(project_name)
    remaining_clarifications = [
        item for item in clarifications if str(item.get("requirement_id", "")) != requirement_id
    ]
    removed_clarifications = len(clarifications) - len(remaining_clarifications)
    _save_pm_clarifications(project_name, remaining_clarifications)

    raw_runs = _load_implementation_runs()
    remaining_runs: list[dict[str, object]] = []
    removed_implementation_runs = 0
    for run in raw_runs:
        if str(run.get("project_name", "")) != project_name or str(run.get("requirement_id", "")) != requirement_id:
            remaining_runs.append(run)
            continue
        removed_implementation_runs += 1
        for artifact_path in (run.get("output_path"), run.get("log_path")):
            if not artifact_path:
                continue
            path = Path(str(artifact_path))
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
    _save_implementation_runs(remaining_runs)

    return RequirementDeletionResult(
        deleted_requirement=matching,
        removed_tasks=removed_tasks,
        updated_tasks=updated_tasks,
        removed_clarifications=removed_clarifications,
        removed_implementation_runs=removed_implementation_runs,
    )


def append_requirement(
    project_name: str,
    title: str,
    description: str,
    *,
    status: str = "NEW",
    priority: str = "MEDIUM",
    effort: str = "M",
) -> RequirementRecord:
    document = load_requirement_document(project_name)
    records = list(document.active_requirements + document.backlog_requirements)
    new_record = RequirementRecord(
        id=next_requirement_id(project_name),
        title=title.strip(),
        status=status.strip(),
        priority=_normalize_priority(priority),
        effort=_normalize_effort(effort),
        description=description.strip(),
    )
    records.append(new_record)
    save_requirement_document(project_name, records, document)
    return new_record


def _priority_rank(value: str) -> int:
    return {"HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(value.strip().upper(), 0)


def _effort_rank(value: str) -> int:
    return {"S": 1, "M": 2, "L": 3}.get(value.strip().upper(), 0)


def _requirement_similarity_tokens(text: str) -> set[str]:
    cleaned = re.sub(r"[^a-z0-9]+", " ", text.lower())
    tokens = {
        token
        for token in cleaned.split()
        if len(token) > 2 and token not in REQUIREMENT_CONSOLIDATION_STOPWORDS
    }
    return tokens


def _find_requirement_consolidation_target(
    project_name: str,
    requirement_title: str,
    requirement_body: str,
) -> RequirementRecord | None:
    document = load_requirement_document(project_name)
    candidates = [
        record
        for record in (document.active_requirements + document.backlog_requirements)
        if record.status != "DONE"
    ]
    incoming_title_tokens = _requirement_similarity_tokens(requirement_title)
    incoming_body_tokens = _requirement_similarity_tokens(requirement_body)
    incoming_tokens = incoming_title_tokens | incoming_body_tokens
    if not incoming_tokens:
        return None

    best_match: RequirementRecord | None = None
    best_score = 0.0
    for candidate in candidates:
        candidate_title_tokens = _requirement_similarity_tokens(candidate.title)
        candidate_body_tokens = _requirement_similarity_tokens(candidate.description)
        candidate_tokens = candidate_title_tokens | candidate_body_tokens
        if not candidate_tokens:
            continue
        shared = incoming_tokens & candidate_tokens
        if len(shared) < 3:
            continue
        score = len(shared) / max(1, min(len(incoming_tokens), len(candidate_tokens)))
        title_overlap = len(incoming_title_tokens & candidate_title_tokens)
        if score < 0.45 and title_overlap < 2:
            continue
        if score > best_score:
            best_match = candidate
            best_score = score
    return best_match


def _merge_review_artifact_into_requirement(
    project_name: str,
    requirement: RequirementRecord,
    *,
    source_agent_name: str,
    artifact_title: str,
    artifact_body: str,
    priority: str,
    effort: str,
) -> RequirementRecord:
    note_header = "**Additional approved review input**"
    note_body = "\n".join(
        [
            note_header,
            f"Source: {source_agent_name}",
            f"Title: {artifact_title.strip() or 'Untitled review'}",
            "",
            artifact_body.strip(),
        ]
    ).strip()
    description = requirement.description.strip()
    if artifact_body.strip() not in description:
        description = f"{description}\n\n{note_body}".strip()

    merged = RequirementRecord(
        id=requirement.id,
        title=requirement.title,
        status=requirement.status,
        priority=priority if _priority_rank(priority) > _priority_rank(requirement.priority) else requirement.priority,
        effort=effort if _effort_rank(effort) > _effort_rank(requirement.effort) else requirement.effort,
        description=description,
    )
    update_requirement(project_name, merged)
    return merged


def move_requirement(project_name: str, requirement_id: str, direction: int) -> None:
    document = load_requirement_document(project_name)
    records = list(document.active_requirements + document.backlog_requirements)
    index = next((i for i, record in enumerate(records) if record.id == requirement_id), None)
    if index is None:
        raise ValueError(f"Requirement not found: {requirement_id}")

    target = index + direction
    if target < 0 or target >= len(records):
        return

    records[index], records[target] = records[target], records[index]
    save_requirement_document(project_name, records, document)


def create_project_from_ui(project_name: str, display_name: str, initial_idea: str) -> Path:
    return scaffold_project(
        project_name=project_name.strip(),
        display_name=display_name.strip(),
        product_title=display_name.strip(),
        initial_requirement=initial_idea.strip(),
    )


def create_project_from_reviewed_draft(
    project_name: str,
    display_name: str,
    requirement_title: str,
    requirement_description: str,
) -> Path:
    normalized_project_name = project_name.strip()
    normalized_display_name = display_name.strip()
    normalized_requirement_title = requirement_title.strip()
    normalized_requirement_description = requirement_description.strip()

    try:
        return scaffold_project(
            project_name=normalized_project_name,
            display_name=normalized_display_name,
            product_title=normalized_display_name,
            initial_requirement_title=normalized_requirement_title,
            initial_requirement=normalized_requirement_description,
        )
    except TypeError as exc:
        if "initial_requirement_title" not in str(exc):
            raise

        destination = scaffold_project(
            project_name=normalized_project_name,
            display_name=normalized_display_name,
            product_title=normalized_display_name,
            initial_requirement=normalized_requirement_description,
        )
        created_project_name = destination.name
        document = load_requirement_document(created_project_name)
        records = list(document.active_requirements + document.backlog_requirements)
        if records:
            first = records[0]
            records[0] = RequirementRecord(
                id=first.id,
                title=normalized_requirement_title or first.title,
                status=first.status,
                priority=first.priority,
                effort=first.effort,
                description=first.description,
            )
            save_requirement_document(created_project_name, records, document)
        return destination


def discovery_plan(idea: str) -> DiscoveryPlan:
    focus = idea.strip() or "this idea"
    lower_focus = focus.lower()
    if any(keyword in lower_focus for keyword in ("ui", "form", "flow", "workflow", "experience", "interaction")):
        return DiscoveryPlan(
            mode="interaction",
            framing="PM is treating this as an interaction and workflow discovery problem, so the next questions focus on where the current experience feels heavy or unclear.",
            questions=(
                DiscoveryQuestion("target_user", f"Who is the primary user for {focus}, and what makes them the right starting point?"),
                DiscoveryQuestion("problem", "What part of the current interaction feels most frustrating or low-value?"),
                DiscoveryQuestion("context", "Where in the current workflow does this friction show up most clearly?"),
                DiscoveryQuestion("constraints", "What should keep the first interaction simple, relevant, and uncluttered?"),
                DiscoveryQuestion("success", "What would make the first interaction feel more genuinely guided after a short period of use?"),
                DiscoveryQuestion("out_of_scope", "What should stay out of scope while we improve this interaction?"),
            ),
        )

    if any(keyword in lower_focus for keyword in ("integration", "sync", "calendar", "api", "import", "export")):
        return DiscoveryPlan(
            mode="integration",
            framing="PM is treating this as an integration-style requirement, so the next questions focus on system boundaries, dependencies, and value of the connection.",
            questions=(
                DiscoveryQuestion("target_user", f"Who most needs {focus}, and why are they the right first user?"),
                DiscoveryQuestion("problem", "What problem exists today because this system is not connected yet?"),
                DiscoveryQuestion("context", "What current workflow or dependency makes this integration worth doing now?"),
                DiscoveryQuestion("constraints", "What technical or operational constraints should shape the first slice?"),
                DiscoveryQuestion("success", "What outcome would prove the integration is useful without overbuilding it?"),
                DiscoveryQuestion("out_of_scope", "What related integration behavior should stay out of the first version?"),
            ),
        )

    return DiscoveryPlan(
        mode="general",
        framing="PM is treating this as a general product-discovery problem, so the next questions focus on user, problem, context, constraints, and success.",
        questions=(
            DiscoveryQuestion("target_user", f"Who is the primary user for {focus}, and what makes them the right starting point?"),
            DiscoveryQuestion("problem", "What user problem are we trying to solve first?"),
            DiscoveryQuestion("context", "What context or current workflow makes this problem worth solving now?"),
            DiscoveryQuestion("constraints", "What constraints or guardrails should shape the first version?"),
            DiscoveryQuestion("success", "What would make the first version feel successful after a short period of use?"),
            DiscoveryQuestion("out_of_scope", "What should stay out of scope for the first version?"),
        ),
    )


def discovery_questions(idea: str) -> tuple[DiscoveryQuestion, ...]:
    return discovery_plan(idea).questions


def experience_intake_plan(user_problem: str) -> ExperienceIntakePlan:
    problem = user_problem.strip().lower()
    recommendation_type = "UX improvement in scope"
    rationale_prompt = "Why should this finding be routed this way?"

    if any(keyword in problem for keyword in ("add", "should be able", "need to", "it will be better", "would be better")):
        recommendation_type = "feature candidate"
        rationale_prompt = "Why does this feel like a feature candidate rather than a small in-scope polish issue?"
    elif any(keyword in problem for keyword in ("scope", "permission", "share", "remote", "collaborator")):
        recommendation_type = "scope escalation"
        rationale_prompt = "Why does this seem to need a scope or strategy decision before PM acts?"

    affected_prompt = "Which user or workflow is feeling this problem most directly?"
    evidence_prompt = "What did you observe that supports this finding?"

    if any(keyword in problem for keyword in ("ui", "form", "layout", "card", "page", "screen")):
        affected_prompt = "Which screen or interaction path is being affected most?"
        evidence_prompt = "What about the current UI or interaction makes this issue visible?"
    elif any(keyword in problem for keyword in ("discovery", "question", "feedback", "intake")):
        affected_prompt = "Which feedback or discovery workflow is becoming heavy or unclear?"
        evidence_prompt = "What about the current intake flow is causing friction?"

    return ExperienceIntakePlan(
        affected_workflow_prompt=affected_prompt,
        evidence_prompt=evidence_prompt,
        rationale_prompt=rationale_prompt,
        recommendation_type=recommendation_type,
    )


def _load_agent_threads() -> list[dict[str, object]]:
    _ensure_agent_thread_store()
    return json.loads(AGENT_THREAD_FILE.read_text())


def _save_agent_threads(raw_threads: list[dict[str, object]]) -> None:
    _ensure_agent_thread_store()
    AGENT_THREAD_FILE.write_text(json.dumps(raw_threads, indent=2))


def _load_experience_findings() -> list[dict[str, object]]:
    _ensure_experience_store()
    return json.loads(EXPERIENCE_FILE.read_text())


def _save_experience_findings(raw_findings: list[dict[str, object]]) -> None:
    _ensure_experience_store()
    EXPERIENCE_FILE.write_text(json.dumps(raw_findings, indent=2))


def _load_implementation_runs() -> list[dict[str, object]]:
    _ensure_implementation_store()
    return json.loads(IMPLEMENTATION_FILE.read_text())


def _save_implementation_runs(raw_runs: list[dict[str, object]]) -> None:
    _ensure_implementation_store()
    IMPLEMENTATION_FILE.write_text(json.dumps(raw_runs, indent=2))


def _load_approvals() -> list[dict[str, object]]:
    _ensure_approval_store()
    return json.loads(APPROVAL_FILE.read_text())


def _save_approvals(raw_items: list[dict[str, object]]) -> None:
    _ensure_approval_store()
    APPROVAL_FILE.write_text(json.dumps(raw_items, indent=2))


def _load_pm_clarifications(project_name: str) -> list[dict[str, object]]:
    path = _pm_clarifications_path(project_name)
    _ensure_pm_clarification_store(project_name)
    return load_pm_clarification_store(path)


def _save_pm_clarifications(project_name: str, raw_items: list[dict[str, object]]) -> None:
    path = _pm_clarifications_path(project_name)
    _ensure_pm_clarification_store(project_name)
    save_pm_clarification_store(path, raw_items)


def _resolve_pm_clarification_raw(project_name: str, clarification_id: str) -> dict[str, object]:
    return resolve_pm_clarification_in_store(_pm_clarifications_path(project_name), clarification_id)


def _implementation_run_from_dict(raw_run: dict[str, object]) -> ImplementationRun:
    worker_pid = raw_run.get("worker_pid")
    return ImplementationRun(
        run_id=str(raw_run["run_id"]),
        project_name=str(raw_run["project_name"]),
        requirement_id=str(raw_run["requirement_id"]),
        requirement_title=str(raw_run.get("requirement_title", "")),
        status=str(raw_run["status"]),
        summary=str(raw_run.get("summary", "")),
        error=str(raw_run.get("error", "")),
        created_at=str(raw_run.get("created_at", "")),
        started_at=str(raw_run.get("started_at", "")),
        finished_at=str(raw_run.get("finished_at", "")),
        output_path=str(raw_run.get("output_path", "")),
        log_path=str(raw_run.get("log_path", "")),
        worker_pid=int(worker_pid) if worker_pid is not None else None,
    )


def _approval_from_dict(raw_item: dict[str, object]) -> ApprovalRequest:
    raw_payload = raw_item.get("payload", {})
    payload = {str(key): str(value) for key, value in dict(raw_payload).items()} if isinstance(raw_payload, dict) else {}
    return ApprovalRequest(
        approval_id=str(raw_item.get("approval_id", "")),
        project_name=str(raw_item.get("project_name", "")),
        approval_type=str(raw_item.get("approval_type", "")),
        source_thread_id=str(raw_item.get("source_thread_id", "")),
        source_agent_name=str(raw_item.get("source_agent_name", "")),
        title=str(raw_item.get("title", "")),
        summary=str(raw_item.get("summary", "")),
        payload=payload,
        status=str(raw_item.get("status", "")),
        created_at=str(raw_item.get("created_at", "")),
        resolved_at=str(raw_item.get("resolved_at", "")),
    )


def _clean_attachment_paths(paths: object) -> tuple[str, ...]:
    if not isinstance(paths, (list, tuple)):
        return ()
    return tuple(str(path) for path in paths if str(path).strip())


def _agent_message_from_dict(message: dict[str, object]) -> AgentMessage:
    return AgentMessage(
        role=str(message.get("role", "")),
        content=str(message.get("content", "")),
        created_at=str(message.get("created_at", "")),
        attachments=_clean_attachment_paths(message.get("attachments", [])),
    )


def _agent_message_payload(message: AgentMessage) -> dict[str, object]:
    return {
        "role": message.role,
        "content": message.content,
        "created_at": message.created_at,
        "attachments": list(message.attachments),
    }


def _agent_message(role: str, content: str, *, attachments: tuple[str, ...] = ()) -> dict[str, object]:
    return {
        "role": role,
        "content": content.strip(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "attachments": list(attachments),
    }


def _slugify_filename(name: str) -> str:
    stem = Path(name).stem or "image"
    suffix = Path(name).suffix.lower()
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem).strip("-") or "image"
    safe_suffix = suffix if re.fullmatch(r"\.[A-Za-z0-9]+", suffix) else ".png"
    return f"{safe_stem}{safe_suffix}"


def save_agent_message_uploads(
    project_name: str,
    thread_id: str,
    image_files: tuple[tuple[str, bytes], ...],
) -> tuple[str, ...]:
    saved_paths: list[str] = []
    if not image_files:
        return ()

    upload_dir = AGENT_UPLOAD_DIR / project_name / thread_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    for original_name, raw_bytes in image_files:
        safe_name = _slugify_filename(original_name or "image.png")
        unique_name = f"{uuid4()}-{safe_name}"
        destination = upload_dir / unique_name
        destination.write_bytes(raw_bytes)
        saved_paths.append(str(destination))
    return tuple(saved_paths)


def _image_path_to_data_url(image_path: str) -> str | None:
    try:
        image_bytes = Path(image_path).read_bytes()
    except OSError:
        return None
    mime_type, _ = mimetypes.guess_type(image_path)
    mime = mime_type or "image/png"
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _agent_thread_from_dict(raw_thread: dict[str, object]) -> AgentThread:
    raw_messages = raw_thread.get("messages", [])
    messages = tuple(
        _agent_message_from_dict(message)
        for message in raw_messages
        if isinstance(message, dict)
    )
    raw_answers = raw_thread.get("answers", {})
    answers = {str(key): str(value) for key, value in dict(raw_answers).items()} if isinstance(raw_answers, dict) else {}
    raw_draft_data = raw_thread.get("draft_data", {})
    draft_data = {str(key): str(value) for key, value in dict(raw_draft_data).items()} if isinstance(raw_draft_data, dict) else {}
    return AgentThread(
        thread_id=str(raw_thread["thread_id"]),
        project_name=str(raw_thread["project_name"]),
        agent_name=str(raw_thread["agent_name"]),
        mode=str(raw_thread["mode"]),
        status=str(raw_thread["status"]),
        idea=str(raw_thread.get("idea", "")),
        planner_type=str(raw_thread.get("planner_type", "hybrid")),
        plan_mode=str(raw_thread.get("plan_mode", "")),
        current_question_index=int(raw_thread.get("current_question_index", 0)),
        current_field_id=str(raw_thread.get("current_field_id", "")),
        answers=answers,
        draft_title=str(raw_thread.get("draft_title", "")),
        draft=str(raw_thread.get("draft", "")),
        draft_data=draft_data,
        messages=messages,
        created_at=str(raw_thread.get("created_at", "")),
        updated_at=str(raw_thread.get("updated_at", "")),
    )


def list_agent_threads(
    project_name: str,
    *,
    agent_name: str | None = None,
    mode: str | None = None,
) -> list[AgentThread]:
    raw_threads = _load_agent_threads()
    project_threads = [thread for thread in raw_threads if thread.get("project_name") == project_name]
    if agent_name is not None:
        project_threads = [thread for thread in project_threads if str(thread.get("agent_name", "")) == agent_name]
    if mode is not None:
        project_threads = [thread for thread in project_threads if str(thread.get("mode", "")) == mode]
    return [
        _agent_thread_from_dict(thread)
        for thread in sorted(project_threads, key=lambda item: str(item.get("updated_at", "")), reverse=True)
    ]


def active_agent_thread(project_name: str, *, agent_name: str, mode: str) -> AgentThread | None:
    return next(
        (
            thread
            for thread in list_agent_threads(project_name, agent_name=agent_name, mode=mode)
            if thread.status == "active"
        ),
        None,
    )


PM_DISCOVERY_OPTIONAL_FIELDS = {"out_of_scope"}
PM_DISCOVERY_MIN_WORDS = {
    "target_user": 2,
    "problem": 5,
    "context": 4,
    "constraints": 3,
    "success": 4,
    "out_of_scope": 2,
}
PM_DISCOVERY_GENERIC_PATTERNS = (
    "not sure",
    "tbd",
    "n/a",
    "no idea",
    "idk",
    "same as above",
    "unsure",
)


def _pm_discovery_words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text)


def _pm_clean_snippet(text: str) -> str:
    return text.strip().rstrip(".!?")


def _pm_answer_sufficient(field_id: str, answer: str) -> bool:
    value = answer.strip()
    if not value:
        return False

    lowered = value.lower()
    if any(pattern in lowered for pattern in PM_DISCOVERY_GENERIC_PATTERNS):
        return False

    words = _pm_discovery_words(value)
    min_words = PM_DISCOVERY_MIN_WORDS.get(field_id, 3)
    if len(words) < min_words:
        return False

    if field_id == "target_user":
        bland_tokens = {"user", "users", "people", "person", "team", "teams", "customer", "customers"}
        return any(token.lower() not in bland_tokens for token in words)

    return True


def _pm_field_prompt(plan: DiscoveryPlan, field_id: str) -> str:
    for question in plan.questions:
        if question.id == field_id:
            return question.prompt
    raise ValueError(f"PM discovery field not found: {field_id}")


def _pm_first_unsatisfied_field(plan: DiscoveryPlan, answers: dict[str, str]) -> str | None:
    for question in plan.questions:
        if not _pm_answer_sufficient(question.id, answers.get(question.id, "")):
            return question.id
    return None


def _pm_known_context_snippet(answers: dict[str, str], field_id: str) -> str:
    if field_id == "problem":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        if target_user:
            return f"For {target_user}, "
    if field_id == "context":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if target_user and problem:
            return f"For {target_user}, around `{problem}`, "
    if field_id == "constraints":
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if problem:
            return f"To solve `{problem}` cleanly, "
    if field_id == "success":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        if target_user:
            return f"For {target_user}, "
    if field_id == "out_of_scope":
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if problem:
            return f"While we improve `{problem}`, "
    return ""


def _pm_follow_up_prompt(plan: DiscoveryPlan, field_id: str, answers: dict[str, str]) -> str:
    prefix = _pm_known_context_snippet(answers, field_id)
    follow_ups = {
        "target_user": "I still need a clearer first user. Who exactly should we optimise for first, and why are they the right starting point?",
        "problem": "I need the sharper user pain here. What concrete frustration or failure are we solving first?",
        "context": "I still need the operating context. Where in the current workflow does this problem show up most clearly?",
        "constraints": "I need the guardrails for the first slice. What should we deliberately keep narrow, local, or simple?",
        "success": "I still need the success test. After a short period of use, what result would make you say this first version is working?",
        "out_of_scope": "I still need the boundary. What tempting adjacent work should stay out of the first version?",
    }
    return f"{prefix}{follow_ups.get(field_id, _pm_field_prompt(plan, field_id))}".strip()


def _pm_next_prompt(plan: DiscoveryPlan, idea: str, answers: dict[str, str], field_id: str) -> str:
    if field_id in answers and answers.get(field_id, "").strip() and not _pm_answer_sufficient(field_id, answers.get(field_id, "")):
        return _pm_follow_up_prompt(plan, field_id, answers)

    if field_id == "problem":
        target_user = _pm_clean_snippet(answers.get("target_user", ""))
        if target_user:
            return f"Got it. For {target_user}, what user problem are we trying to solve first?"
    if field_id == "context":
        problem = _pm_clean_snippet(answers.get("problem", ""))
        if problem:
            return f"Thanks. Where does `{problem}` show up in the current workflow, and why is it worth solving now?"
    if field_id == "constraints":
        return "What constraints or guardrails should shape the first version so we learn without overbuilding it?"
    if field_id == "success":
        return "If we get the first slice right, what outcome would make this feel successful after a short period of use?"
    if field_id == "out_of_scope":
        return "Before I draft, what should stay clearly out of scope for the first version?"
    return _pm_field_prompt(plan, field_id)


def _build_pm_discovery_intro(idea: str, plan: DiscoveryPlan) -> str:
    focus = idea.strip() or "this idea"
    opening = (
        f"Got it. I’m treating `{focus}` as a {plan.mode} discovery problem. "
        "I’ll track what we already know, only ask the next question that matters, and draft requirements when I have enough context."
    )
    first_field = _pm_first_unsatisfied_field(plan, {})
    if not first_field:
        return opening
    return f"{opening}\n\n{_pm_next_prompt(plan, idea, {}, first_field)}"


def _pm_draft_ready(answers: dict[str, str], plan: DiscoveryPlan) -> bool:
    for question in plan.questions:
        if question.id in PM_DISCOVERY_OPTIONAL_FIELDS:
            continue
        if not _pm_answer_sufficient(question.id, answers.get(question.id, "")):
            return False
    return True


def _generate_pm_thread_draft(raw_thread: dict[str, object]) -> str:
    return build_discovery_draft(
        str(raw_thread.get("project_name", "")),
        str(raw_thread.get("idea", "")),
        {str(key): str(value) for key, value in dict(raw_thread.get("answers", {})).items()},
    )


def _agent_thread_messages(raw_thread: dict[str, object]) -> tuple[AgentMessage, ...]:
    raw_messages = raw_thread.get("messages", [])
    return tuple(
        _agent_message_from_dict(message)
        for message in raw_messages
        if isinstance(message, dict)
    )


def _pm_thread_label(raw_thread: dict[str, object]) -> str:
    idea = str(raw_thread.get("idea", "")).strip()
    if not idea:
        return "PM discovery thread"
    trimmed = idea[:72].rstrip()
    return trimmed if len(idea) <= 72 else f"{trimmed}..."


def _create_or_replace_pm_thread_clarification(
    project_name: str,
    raw_thread: dict[str, object],
    *,
    summary: str,
    questions: list[str],
) -> PMClarification:
    raw_items = _load_pm_clarifications(project_name)
    source_thread_id = str(raw_thread.get("thread_id", ""))
    remaining = [
        item
        for item in raw_items
        if not (
            str(item.get("source_thread_id", "")) == source_thread_id
            and str(item.get("status", "")) == "OPEN"
        )
    ]
    _save_pm_clarifications(project_name, remaining)
    return save_pm_clarification(
        project_name,
        requirement_id="",
        requirement_title=_pm_thread_label(raw_thread),
        source_thread_id=source_thread_id,
        summary=summary,
        questions=questions,
    )


def _apply_live_pm_turn_to_thread(
    project_name: str,
    matching: dict[str, object],
    turn: LivePMTurn,
) -> None:
    matching.setdefault("messages", [])
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))

    if turn.next_action == "draft_requirements":
        matching["draft_title"] = turn.draft_title.strip()
        matching["draft"] = turn.draft_requirement.strip()
        matching["status"] = "active"
        return

    if turn.next_action == "request_clarification":
        summary = turn.clarification_summary.strip() or "PM needs clarification before it can draft responsibly."
        questions = [question.strip() for question in turn.clarification_questions if question.strip()]
        if not questions:
            raise LivePMDiscoveryError("PM requested a clarification without any clarification questions.")
        _create_or_replace_pm_thread_clarification(
            project_name,
            matching,
            summary=summary,
            questions=questions,
        )
        matching["status"] = "blocked_clarification"
        return

    matching["status"] = "active"


def start_pm_requirement_discovery_thread(
    project_name: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    _archive_active_agent_threads(
        project_name,
        raw_threads,
        agent_name="PM",
        mode="Requirement Discovery",
    )
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    thread_messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_pm_turn(project_name, project_name, thread_messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    raw_thread = {
        "thread_id": thread_id,
        "project_name": project_name,
        "agent_name": "PM",
        "mode": "Requirement Discovery",
        "status": "active",
        "idea": idea.strip(),
        "planner_type": "live",
        "plan_mode": "live",
        "current_question_index": 0,
        "current_field_id": "",
        "answers": {},
        "draft_title": turn.draft_title.strip() if turn.next_action == "draft_requirements" else "",
        "draft": turn.draft_requirement.strip() if turn.next_action == "draft_requirements" else "",
        "draft_data": {},
        "messages": [_agent_message("user", idea.strip(), attachments=attachments)],
        "created_at": created_at,
        "updated_at": updated_at,
    }
    _apply_live_pm_turn_to_thread(project_name, raw_thread, turn)
    raw_threads.append(raw_thread)
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(raw_thread)


def reply_to_pm_requirement_discovery_thread(
    project_name: str,
    thread_id: str,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    if str(matching.get("status", "")) != "active":
        raise ValueError(f"Agent thread is not active: {thread_id}")

    matching.setdefault("messages", [])
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    matching["messages"].append(_agent_message("user", reply, attachments=attachments))
    matching["status"] = "active"
    turn = _run_live_pm_turn(
        project_name,
        project_name,
        _agent_thread_messages(matching),
    )
    _apply_live_pm_turn_to_thread(project_name, matching, turn)
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def draft_pm_requirement_discovery_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")

    turn = _run_live_pm_turn(
        project_name,
        project_name,
        _agent_thread_messages(matching),
        force_draft=True,
    )
    _apply_live_pm_turn_to_thread(project_name, matching, turn)
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def save_pm_requirement_thread_to_requirements(
    project_name: str,
    thread_id: str,
    requirement_title: str,
    *,
    status: str,
    priority: str,
    effort: str,
) -> RequirementRecord:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")

    draft = str(matching.get("draft", "")).strip()
    if not draft:
        raise ValueError(f"Thread has no draft requirements yet: {thread_id}")

    record = append_requirement(
        project_name,
        requirement_title,
        draft,
        status=status,
        priority=priority,
        effort=effort,
    )
    matching["status"] = "saved"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return record


def request_pm_requirement_thread_approval(
    project_name: str,
    thread_id: str,
    *,
    requirement_title: str,
    status: str,
    priority: str,
    effort: str,
) -> ApprovalRequest:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "PM"
            and thread.get("mode") == "Requirement Discovery"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft = str(matching.get("draft", "")).strip()
    if not draft:
        raise ValueError(f"Thread has no draft requirements yet: {thread_id}")
    approval = _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="requirement_draft",
        source_thread_id=thread_id,
        source_agent_name="PM",
        title=requirement_title.strip(),
        summary="Approve this PM draft to save it into product/requirements.md.",
        payload={
            "requirement_title": requirement_title.strip(),
            "status": status.strip(),
            "priority": priority.strip(),
            "effort": effort.strip(),
            "draft": draft,
        },
    )
    matching["status"] = "pending_approval"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return approval


def archive_agent_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name and thread.get("thread_id") == thread_id
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    matching["status"] = "archived"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def list_approvals(project_name: str | None = None) -> list[ApprovalRequest]:
    raw_items = _load_approvals()
    approvals = [_approval_from_dict(item) for item in raw_items if isinstance(item, dict)]
    if project_name is not None:
        approvals = [item for item in approvals if item.project_name == project_name]
    return sorted(approvals, key=lambda item: item.created_at, reverse=True)


def active_approvals(project_name: str | None = None) -> list[ApprovalRequest]:
    return [item for item in list_approvals(project_name) if item.status == "OPEN"]


def _create_or_replace_thread_approval(
    *,
    project_name: str,
    approval_type: str,
    source_thread_id: str,
    source_agent_name: str,
    title: str,
    summary: str,
    payload: dict[str, str],
) -> ApprovalRequest:
    raw_items = _load_approvals()
    remaining = [
        item
        for item in raw_items
        if not (
            str(item.get("project_name", "")) == project_name
            and str(item.get("source_thread_id", "")) == source_thread_id
            and str(item.get("status", "")) == "OPEN"
        )
    ]
    created_at = datetime.now(timezone.utc).isoformat()
    approval = {
        "approval_id": str(uuid4()),
        "project_name": project_name,
        "approval_type": approval_type,
        "source_thread_id": source_thread_id,
        "source_agent_name": source_agent_name,
        "title": title.strip(),
        "summary": summary.strip(),
        "payload": payload,
        "status": "OPEN",
        "created_at": created_at,
        "resolved_at": "",
    }
    remaining.append(approval)
    _save_approvals(remaining)
    return _approval_from_dict(approval)


def _approval_outcome_payload(result: RequirementRecord | ApprovalRequest) -> dict[str, str]:
    if isinstance(result, RequirementRecord):
        return {
            "outcome_kind": "requirement",
            "outcome_title": result.title,
            "outcome_reference_id": result.id,
            "outcome_detail": f"Continued into backlog requirement {result.id}.",
        }
    return {
        "outcome_kind": "approval",
        "outcome_title": result.title,
        "outcome_reference_id": result.approval_id,
        "outcome_detail": "Continued into an explicit scope confirmation.",
    }


LIVE_PM_DEFAULT_MODEL = os.getenv("OPENAI_PM_LIVE_MODEL", "gpt-4o-mini")
LIVE_AGENT_DEFAULT_MODEL = os.getenv("OPENAI_AGENT_LIVE_MODEL", LIVE_PM_DEFAULT_MODEL)


def _live_pm_system_prompt(project_name: str, display_name: str, *, force_draft: bool) -> str:
    force_line = (
        "You must now draft the initial requirement, even if some uncertainty remains. Put any uncertainty into the draft's open questions."
        if force_draft
        else "Ask exactly one next clarifying question when you still need meaningful context. Draft only when you genuinely have enough."
    )
    return (
        "You are the Product Manager for AI Builder OS in Requirement Discovery Mode.\n"
        f"You are helping shape a brand-new project called `{display_name}` (`{project_name}`).\n"
        "Work like a real PM: understand the user, problem, context, constraints, and success before drafting.\n"
        "Be concise, specific, and genuinely responsive to the prior messages.\n"
        "When the user shares images, use them as real context for the conversation instead of ignoring them.\n"
        "Do not ask a fixed questionnaire. Ask only the next most relevant question.\n"
        "If the user has already answered something implicitly, do not ask for it again.\n"
        "If a materially blocking ambiguity remains around scope boundary, concurrency, ownership, system boundary, failure handling, or success criteria, "
        "you may choose `request_clarification` instead of `ask_question`. Use that only when the ambiguity should become a durable inbox item rather than a normal next-turn question.\n"
        f"{force_line}\n"
        "When you draft, produce exactly one strong initial requirement for the new project.\n"
        "The draft requirement body should use these headings exactly:\n"
        "Problem statement\nTarget user\nCore job-to-be-done\nSuccess criteria\nConstraints\nOut of scope\nAssumptions\nOpen questions"
    )


def _message_to_live_pm_input(message: AgentMessage) -> dict[str, object]:
    role = message.role if message.role in {"user", "assistant", "developer", "system"} else "user"
    if message.attachments and role == "user":
        content: list[dict[str, str]] = [{"type": "input_text", "text": message.content}]
        for image_path in message.attachments:
            data_url = _image_path_to_data_url(image_path)
            if data_url is None:
                continue
            content.append({"type": "input_image", "image_url": data_url})
        return {"role": role, "content": content}
    return {"role": role, "content": message.content}


def _get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise LivePMDiscoveryError("OPENAI_API_KEY is not set. Add it to your environment before using live PM discovery.")
    from openai import OpenAI  # local import keeps non-live paths lightweight

    return OpenAI(api_key=api_key)


def _run_live_pm_turn(
    project_name: str,
    display_name: str,
    messages: tuple[AgentMessage, ...],
    *,
    force_draft: bool = False,
) -> LivePMTurn:
    client = _get_openai_client()
    response = client.responses.parse(
        model=LIVE_PM_DEFAULT_MODEL,
        input=[
            {"role": "developer", "content": _live_pm_system_prompt(project_name, display_name, force_draft=force_draft)},
            *[_message_to_live_pm_input(message) for message in messages],
        ],
        text_format=LivePMTurn,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        raise LivePMDiscoveryError("OpenAI did not return a structured PM discovery response.")
    return parsed


def _live_experience_system_prompt(project_name: str, mode: str, *, force_draft: bool) -> str:
    mode_guidance = {
        "Feedback Synthesis": (
            "Your job is to turn UX feedback, workflow friction, or user pain into one structured finding that can be routed into the OS."
        ),
        "Usability Review": (
            "Your job is to review a UI or flow for usability, clarity, hierarchy, scanability, and workflow friction, then turn that into one structured finding."
        ),
    }
    force_line = (
        "You must now draft the strongest finding you can from the current context, and put any remaining uncertainty into the rationale."
        if force_draft
        else "Ask exactly one next clarifying question when meaningful uncertainty remains. Draft only when you have enough to write one strong finding."
    )
    return (
        "You are the Experience Designer for AI Builder OS.\n"
        f"You are working inside project `{project_name}` in mode `{mode}`.\n"
        f"{mode_guidance.get(mode, mode_guidance['Feedback Synthesis'])}\n"
        "Be concise, genuinely responsive to prior messages, and do not ask a fixed questionnaire.\n"
        "When the user shares images, use them as real evidence for the usability or experience discussion.\n"
        "Prioritise usability problems, comprehension gaps, and workflow friction over purely aesthetic commentary.\n"
        "When you draft, produce exactly one structured finding and classify it as one of:\n"
        "- UX improvement in scope\n"
        "- feature candidate\n"
        "- scope escalation\n"
        f"{force_line}\n"
        "The finding draft should use these headings exactly:\n"
        "User problem\nAffected workflow\nEvidence\nConfidence\nSeverity / frequency\nRecommendation type\nRationale\nRecommended next role"
    )


def _run_live_experience_turn(
    project_name: str,
    mode: str,
    messages: tuple[AgentMessage, ...],
    *,
    force_draft: bool = False,
) -> LiveExperienceTurn:
    client = _get_openai_client()
    response = client.responses.parse(
        model=LIVE_AGENT_DEFAULT_MODEL,
        input=[
            {"role": "developer", "content": _live_experience_system_prompt(project_name, mode, force_draft=force_draft)},
            *[_message_to_live_pm_input(message) for message in messages],
        ],
        text_format=LiveExperienceTurn,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        raise LivePMDiscoveryError("OpenAI did not return a structured Experience Designer response.")
    return parsed


def _live_ui_designer_system_prompt(project_name: str, mode: str, *, force_draft: bool) -> str:
    mode_guidance = {
        "Design Direction": (
            "Your job is to help shape the intended visual system, aesthetics, interaction design, layout approach, and look-and-feel of a user-facing surface before implementation is settled."
        ),
        "UI Review": (
            "Your job is to critique an existing UI that already exists and identify concrete improvements in hierarchy, spacing, composition, visual consistency, and polish."
        ),
    }
    force_line = (
        "You must now draft one concise design brief from the current context, even if some uncertainty remains."
        if force_draft
        else "Ask exactly one next clarifying question when meaningful design uncertainty remains. Draft only when you have enough to propose one strong design brief."
    )
    return (
        "You are the UI Designer for AI Builder OS.\n"
        f"You are working inside project `{project_name}` in mode `{mode}`.\n"
        f"{mode_guidance.get(mode, mode_guidance['Design Direction'])}\n"
        "Focus on usable visual direction, layout, and interface quality rather than vague taste commentary.\n"
        "When the user shares images, use them as real visual context for your critique or design direction.\n"
        "Keep the mode boundary crisp: Design Direction is forward-looking target-state guidance, while UI Review is critique of an existing surface.\n"
        "Do not ask a fixed questionnaire.\n"
        f"{force_line}\n"
        "When you draft, produce exactly one design brief.\n"
        "The design brief should use these headings exactly:\n"
        "Design goal\nUser and context\nVisual direction\nLayout and interaction guidance\nSurface changes\nConstraints\nOpen questions"
    )


def _run_live_ui_designer_turn(
    project_name: str,
    mode: str,
    messages: tuple[AgentMessage, ...],
    *,
    force_draft: bool = False,
) -> LiveUIDesignTurn:
    client = _get_openai_client()
    response = client.responses.parse(
        model=LIVE_AGENT_DEFAULT_MODEL,
        input=[
            {"role": "developer", "content": _live_ui_designer_system_prompt(project_name, mode, force_draft=force_draft)},
            *[_message_to_live_pm_input(message) for message in messages],
        ],
        text_format=LiveUIDesignTurn,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        raise LivePMDiscoveryError("OpenAI did not return a structured UI Designer response.")
    return parsed


def _live_pm_review_completion_system_prompt(project_name: str, artifact_type: str) -> str:
    artifact_label = "approved workflow artifact"
    if artifact_type == "experience_finding":
        artifact_label = "approved Experience Designer finding"
    elif artifact_type == "design_brief":
        artifact_label = "approved UI Designer design brief"

    return (
        "You are the Product Manager for AI Builder OS.\n"
        f"You are reviewing one {artifact_label} inside project `{project_name}`.\n"
        "Your job is to finish the workflow so approved review output becomes actionable.\n"
        "Decide between exactly two outcomes:\n"
        "- `create_backlog_requirement` when the approved artifact should become a real backlog requirement inside this project.\n"
        "- `confirm_out_of_scope` when the approved artifact should not enter backlog without explicit Product Director confirmation.\n"
        "Choose `confirm_out_of_scope` only when the work is truly outside the product scope, too broad, or misaligned with the current product direction.\n"
        "When you choose `create_backlog_requirement`, draft exactly one strong backlog requirement using these headings exactly:\n"
        "Problem statement\nTarget user\nCore job-to-be-done\nSuccess criteria\nConstraints\nOut of scope\nAssumptions\nOpen questions\n"
        "When you choose `confirm_out_of_scope`, provide a concise title and summary that explains why Product Director confirmation is needed.\n"
        "Be concise, specific, and results-oriented."
    )


def _run_live_pm_review_completion_turn(
    project_name: str,
    artifact_type: str,
    artifact_title: str,
    artifact_body: str,
) -> LivePMReviewCompletionTurn:
    client = _get_openai_client()
    response = client.responses.parse(
        model=LIVE_PM_DEFAULT_MODEL,
        input=[
            {"role": "developer", "content": _live_pm_review_completion_system_prompt(project_name, artifact_type)},
            {"role": "user", "content": f"Artifact title: {artifact_title.strip() or 'Untitled artifact'}"},
            {"role": "user", "content": artifact_body.strip()},
        ],
        text_format=LivePMReviewCompletionTurn,
    )
    parsed = getattr(response, "output_parsed", None)
    if parsed is None:
        raise LivePMDiscoveryError("OpenAI did not return a structured PM review completion response.")
    return parsed


def _live_pm_thread_from_dict(raw_thread: dict[str, object]) -> LivePMProjectThread:
    raw_messages = raw_thread.get("messages", [])
    messages = tuple(
        _agent_message_from_dict(message)
        for message in raw_messages
        if isinstance(message, dict)
    )
    return LivePMProjectThread(
        thread_id=str(raw_thread["thread_id"]),
        project_name=str(raw_thread["project_name"]),
        display_name=str(raw_thread["display_name"]),
        planner_type=str(raw_thread.get("planner_type", "live")),
        status=str(raw_thread["status"]),
        messages=messages,
        draft_title=str(raw_thread.get("draft_title", "")),
        draft_requirement=str(raw_thread.get("draft_requirement", "")),
        created_at=str(raw_thread.get("created_at", "")),
        updated_at=str(raw_thread.get("updated_at", "")),
    )


def start_live_pm_project_thread(
    project_name: str,
    display_name: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> LivePMProjectThread:
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_pm_turn(project_name, display_name, messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    draft_title = turn.draft_title.strip() if turn.next_action == "draft_requirements" else ""
    draft_requirement = turn.draft_requirement.strip() if turn.next_action == "draft_requirements" else ""
    return LivePMProjectThread(
        thread_id=thread_id,
        project_name=project_name.strip(),
        display_name=display_name.strip(),
        planner_type="live",
        status="drafted" if draft_requirement else "active",
        messages=(
            *messages,
            AgentMessage(role="assistant", content=turn.assistant_message.strip(), created_at=updated_at),
        ),
        draft_title=draft_title,
        draft_requirement=draft_requirement,
        created_at=created_at,
        updated_at=updated_at,
    )


def continue_live_pm_project_thread(
    thread: LivePMProjectThread,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> LivePMProjectThread:
    user_message = AgentMessage(
        role="user",
        content=reply.strip(),
        created_at=datetime.now(timezone.utc).isoformat(),
        attachments=save_agent_message_uploads(thread.project_name, thread.thread_id, image_files),
    )
    messages = (*thread.messages, user_message)
    turn = _run_live_pm_turn(thread.project_name, thread.display_name, messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    draft_title = turn.draft_title.strip() if turn.next_action == "draft_requirements" else thread.draft_title
    draft_requirement = turn.draft_requirement.strip() if turn.next_action == "draft_requirements" else thread.draft_requirement
    return LivePMProjectThread(
        thread_id=thread.thread_id,
        project_name=thread.project_name,
        display_name=thread.display_name,
        planner_type=thread.planner_type,
        status="drafted" if draft_requirement else "active",
        messages=(
            *messages,
            AgentMessage(role="assistant", content=turn.assistant_message.strip(), created_at=updated_at),
        ),
        draft_title=draft_title,
        draft_requirement=draft_requirement,
        created_at=thread.created_at,
        updated_at=updated_at,
    )


def draft_live_pm_project_thread(thread: LivePMProjectThread) -> LivePMProjectThread:
    turn = _run_live_pm_turn(thread.project_name, thread.display_name, thread.messages, force_draft=True)
    updated_at = datetime.now(timezone.utc).isoformat()
    return LivePMProjectThread(
        thread_id=thread.thread_id,
        project_name=thread.project_name,
        display_name=thread.display_name,
        planner_type=thread.planner_type,
        status="drafted",
        messages=(
            *thread.messages,
            AgentMessage(role="assistant", content=turn.assistant_message.strip(), created_at=updated_at),
        ),
        draft_title=turn.draft_title.strip(),
        draft_requirement=turn.draft_requirement.strip(),
        created_at=thread.created_at,
        updated_at=updated_at,
    )


def start_experience_designer_thread(
    project_name: str,
    mode: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    _archive_active_agent_threads(project_name, raw_threads, agent_name="Experience Designer", mode=mode)
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_experience_turn(project_name, mode, messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    raw_thread = {
        "thread_id": thread_id,
        "project_name": project_name,
        "agent_name": "Experience Designer",
        "mode": mode,
        "status": "active",
        "idea": idea.strip(),
        "planner_type": "live",
        "plan_mode": "live",
        "current_question_index": 0,
        "current_field_id": "",
        "answers": {},
        "draft_title": "Experience finding draft" if turn.next_action == "draft_finding" else "",
        "draft": turn.finding_draft.strip() if turn.next_action == "draft_finding" else "",
        "draft_data": {
            "user_problem": turn.user_problem.strip(),
            "affected_workflow": turn.affected_workflow.strip(),
            "evidence": turn.evidence.strip(),
            "confidence": turn.confidence.strip(),
            "severity": turn.severity.strip(),
            "frequency": turn.frequency.strip(),
            "recommendation_type": turn.recommendation_type.strip(),
            "rationale": turn.rationale.strip(),
        }
        if turn.next_action == "draft_finding"
        else {},
        "messages": [
            _agent_message("user", idea.strip(), attachments=attachments),
            _agent_message("assistant", turn.assistant_message.strip()),
        ],
        "created_at": created_at,
        "updated_at": updated_at,
    }
    raw_threads.append(raw_thread)
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(raw_thread)


def reply_to_experience_designer_thread(
    project_name: str,
    thread_id: str,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    if str(matching.get("status", "")) != "active":
        raise ValueError(f"Agent thread is not active: {thread_id}")
    matching.setdefault("messages", [])
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    matching["messages"].append(_agent_message("user", reply, attachments=attachments))
    turn = _run_live_experience_turn(project_name, str(matching.get("mode", "")), _agent_thread_messages(matching))
    if turn.next_action == "draft_finding":
        matching["draft_title"] = "Experience finding draft"
        matching["draft"] = turn.finding_draft.strip()
        matching["draft_data"] = {
            "user_problem": turn.user_problem.strip(),
            "affected_workflow": turn.affected_workflow.strip(),
            "evidence": turn.evidence.strip(),
            "confidence": turn.confidence.strip(),
            "severity": turn.severity.strip(),
            "frequency": turn.frequency.strip(),
            "recommendation_type": turn.recommendation_type.strip(),
            "rationale": turn.rationale.strip(),
        }
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def draft_experience_designer_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    turn = _run_live_experience_turn(
        project_name,
        str(matching.get("mode", "")),
        _agent_thread_messages(matching),
        force_draft=True,
    )
    matching["draft_title"] = "Experience finding draft"
    matching["draft"] = turn.finding_draft.strip()
    matching["draft_data"] = {
        "user_problem": turn.user_problem.strip(),
        "affected_workflow": turn.affected_workflow.strip(),
        "evidence": turn.evidence.strip(),
        "confidence": turn.confidence.strip(),
        "severity": turn.severity.strip(),
        "frequency": turn.frequency.strip(),
        "recommendation_type": turn.recommendation_type.strip(),
        "rationale": turn.rationale.strip(),
    }
    matching.setdefault("messages", [])
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def save_experience_thread_to_finding(project_name: str, thread_id: str) -> ExperienceFinding:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft_data = matching.get("draft_data", {})
    if not isinstance(draft_data, dict) or not draft_data:
        raise ValueError(f"Thread has no experience finding draft yet: {thread_id}")
    finding = save_experience_finding(
        project_name,
        user_problem=str(draft_data.get("user_problem", "")),
        affected_workflow=str(draft_data.get("affected_workflow", "")),
        evidence=str(draft_data.get("evidence", "")),
        confidence=str(draft_data.get("confidence", "MEDIUM")),
        severity=str(draft_data.get("severity", "MEDIUM")),
        frequency=str(draft_data.get("frequency", "MEDIUM")),
        recommendation_type=str(draft_data.get("recommendation_type", "UX improvement in scope")),
        rationale=str(draft_data.get("rationale", "")),
    )
    matching["status"] = "saved"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return finding


def _experience_finding_pm_review_body(finding: ExperienceFinding) -> str:
    return "\n".join(
        [
            "Approved Experience Designer finding:",
            f"User problem: {finding.user_problem}",
            f"Affected workflow: {finding.affected_workflow}",
            f"Evidence: {finding.evidence}",
            f"Confidence: {finding.confidence}",
            f"Severity: {finding.severity}",
            f"Frequency: {finding.frequency}",
            f"Recommendation type: {finding.recommendation_type}",
            f"Rationale: {finding.rationale}",
            f"Recommended next role: {finding.recommended_next_role}",
        ]
    )


def _design_brief_pm_review_body(title: str, draft: str) -> str:
    return "\n".join(
        [
            f"Approved UI Designer brief: {title.strip() or 'Untitled design brief'}",
            "",
            draft.strip(),
        ]
    ).strip()


def _request_scope_confirmation(
    project_name: str,
    *,
    source_thread_id: str,
    source_agent_name: str,
    title: str,
    summary: str,
    payload: dict[str, str],
) -> ApprovalRequest:
    return _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="scope_confirmation",
        source_thread_id=source_thread_id,
        source_agent_name=source_agent_name,
        title=title.strip(),
        summary=summary.strip(),
        payload=payload,
    )


def _complete_review_artifact_with_pm(
    project_name: str,
    *,
    artifact_type: str,
    source_thread_id: str,
    source_agent_name: str,
    artifact_title: str,
    artifact_body: str,
    finding_id: str = "",
) -> RequirementRecord | ApprovalRequest:
    turn = _run_live_pm_review_completion_turn(
        project_name,
        artifact_type,
        artifact_title,
        artifact_body,
    )
    if turn.next_action == "create_backlog_requirement":
        requirement_title = turn.requirement_title.strip() or artifact_title.strip() or "Follow-up requirement"
        requirement_body = turn.requirement_body.strip() or artifact_body.strip()
        target = _find_requirement_consolidation_target(project_name, requirement_title, requirement_body)
        if target is None:
            requirement = append_requirement(
                project_name,
                requirement_title,
                requirement_body,
                status="BACKLOG",
                priority=turn.priority,
                effort=turn.effort,
            )
        else:
            requirement = _merge_review_artifact_into_requirement(
                project_name,
                target,
                source_agent_name=source_agent_name,
                artifact_title=requirement_title,
                artifact_body=requirement_body,
                priority=turn.priority,
                effort=turn.effort,
            )
        if finding_id:
            set_experience_handoff_state(project_name, finding_id, "resolved")
        return requirement

    confirmation_payload = {
        "requirement_title": turn.requirement_title.strip(),
        "requirement_body": turn.requirement_body.strip(),
        "priority": turn.priority,
        "effort": turn.effort,
        "artifact_type": artifact_type,
        "finding_id": finding_id.strip(),
    }
    return _request_scope_confirmation(
        project_name,
        source_thread_id=source_thread_id,
        source_agent_name="PM",
        title=turn.scope_confirmation_title.strip() or f"Confirm out-of-scope outcome for {artifact_title.strip() or source_agent_name}",
        summary=turn.scope_confirmation_summary.strip()
        or "PM believes this approved review should stay out of the current project scope unless Product Director says otherwise.",
        payload=confirmation_payload,
    )


def request_experience_thread_approval(project_name: str, thread_id: str) -> ApprovalRequest:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "Experience Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft_data = matching.get("draft_data", {})
    if not isinstance(draft_data, dict) or not draft_data:
        raise ValueError(f"Thread has no experience finding draft yet: {thread_id}")
    approval = _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="experience_finding",
        source_thread_id=thread_id,
        source_agent_name="Experience Designer",
        title="Approve Experience Designer finding",
        summary="Approve this reviewed finding to save it and continue it through PM completion.",
        payload={str(key): str(value) for key, value in draft_data.items()},
    )
    matching["status"] = "pending_approval"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return approval


def start_ui_designer_thread(
    project_name: str,
    mode: str,
    idea: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    _archive_active_agent_threads(project_name, raw_threads, agent_name="UI Designer", mode=mode)
    created_at = datetime.now(timezone.utc).isoformat()
    thread_id = str(uuid4())
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    messages = (
        AgentMessage(role="user", content=idea.strip(), created_at=created_at, attachments=attachments),
    )
    turn = _run_live_ui_designer_turn(project_name, mode, messages)
    updated_at = datetime.now(timezone.utc).isoformat()
    raw_thread = {
        "thread_id": thread_id,
        "project_name": project_name,
        "agent_name": "UI Designer",
        "mode": mode,
        "status": "active",
        "idea": idea.strip(),
        "planner_type": "live",
        "plan_mode": "live",
        "current_question_index": 0,
        "current_field_id": "",
        "answers": {},
        "draft_title": turn.draft_title.strip() if turn.next_action == "draft_design_brief" else "",
        "draft": turn.design_brief.strip() if turn.next_action == "draft_design_brief" else "",
        "draft_data": {},
        "messages": [
            _agent_message("user", idea.strip(), attachments=attachments),
            _agent_message("assistant", turn.assistant_message.strip()),
        ],
        "created_at": created_at,
        "updated_at": updated_at,
    }
    raw_threads.append(raw_thread)
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(raw_thread)


def reply_to_ui_designer_thread(
    project_name: str,
    thread_id: str,
    reply: str,
    *,
    image_files: tuple[tuple[str, bytes], ...] = (),
) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "UI Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    if str(matching.get("status", "")) != "active":
        raise ValueError(f"Agent thread is not active: {thread_id}")
    matching.setdefault("messages", [])
    attachments = save_agent_message_uploads(project_name, thread_id, image_files)
    matching["messages"].append(_agent_message("user", reply, attachments=attachments))
    turn = _run_live_ui_designer_turn(project_name, str(matching.get("mode", "")), _agent_thread_messages(matching))
    if turn.next_action == "draft_design_brief":
        matching["draft_title"] = turn.draft_title.strip()
        matching["draft"] = turn.design_brief.strip()
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def draft_ui_designer_thread(project_name: str, thread_id: str) -> AgentThread:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "UI Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    turn = _run_live_ui_designer_turn(
        project_name,
        str(matching.get("mode", "")),
        _agent_thread_messages(matching),
        force_draft=True,
    )
    matching["draft_title"] = turn.draft_title.strip()
    matching["draft"] = turn.design_brief.strip()
    matching.setdefault("messages", [])
    matching["messages"].append(_agent_message("assistant", turn.assistant_message.strip()))
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return _agent_thread_from_dict(matching)


def request_ui_design_brief_approval(project_name: str, thread_id: str) -> ApprovalRequest:
    raw_threads = _load_agent_threads()
    matching = next(
        (
            thread
            for thread in raw_threads
            if thread.get("project_name") == project_name
            and thread.get("thread_id") == thread_id
            and thread.get("agent_name") == "UI Designer"
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Agent thread not found: {thread_id}")
    draft = str(matching.get("draft", "")).strip()
    if not draft:
        raise ValueError(f"Thread has no design brief draft yet: {thread_id}")
    approval = _create_or_replace_thread_approval(
        project_name=project_name,
        approval_type="design_brief",
        source_thread_id=thread_id,
        source_agent_name="UI Designer",
        title=str(matching.get("draft_title", "")).strip() or "Approve UI design brief",
        summary="Approve this design brief to continue it through PM completion into backlog or scope confirmation.",
        payload={"draft": draft},
    )
    matching["status"] = "pending_approval"
    matching["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return approval


def approve_request(project_name: str, approval_id: str) -> ApprovalRequest:
    raw_items = _load_approvals()
    matching = next(
        (
            item
            for item in raw_items
            if str(item.get("approval_id", "")) == approval_id and str(item.get("project_name", "")) == project_name
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Approval not found: {approval_id}")
    if str(matching.get("status", "")) != "OPEN":
        raise ValueError(f"Approval is not open: {approval_id}")

    approval = _approval_from_dict(matching)
    outcome_payload: dict[str, str] = {}
    if approval.approval_type == "requirement_draft":
        record = save_pm_requirement_thread_to_requirements(
            project_name,
            approval.source_thread_id,
            approval.payload.get("requirement_title", approval.title),
            status=approval.payload.get("status", "NEW"),
            priority=approval.payload.get("priority", "MEDIUM"),
            effort=approval.payload.get("effort", "M"),
        )
        outcome_payload = {
            "outcome_kind": "requirement",
            "outcome_title": record.title,
            "outcome_reference_id": record.id,
            "outcome_detail": f"Saved into requirements.md as {record.id} ({record.status}).",
        }
    elif approval.approval_type == "experience_finding":
        finding = save_experience_thread_to_finding(project_name, approval.source_thread_id)
        result = _complete_review_artifact_with_pm(
            project_name,
            artifact_type="experience_finding",
            source_thread_id=approval.source_thread_id,
            source_agent_name=approval.source_agent_name,
            artifact_title="Approved Experience Designer finding",
            artifact_body=_experience_finding_pm_review_body(finding),
            finding_id=finding.finding_id,
        )
        outcome_payload = _approval_outcome_payload(result)
    elif approval.approval_type == "design_brief":
        draft = approval.payload.get("draft", "").strip()
        result = _complete_review_artifact_with_pm(
            project_name,
            artifact_type="design_brief",
            source_thread_id=approval.source_thread_id,
            source_agent_name=approval.source_agent_name,
            artifact_title=approval.title,
            artifact_body=_design_brief_pm_review_body(approval.title, draft),
        )
        outcome_payload = _approval_outcome_payload(result)
        archive_agent_thread(project_name, approval.source_thread_id)
    elif approval.approval_type == "scope_confirmation":
        finding_id = approval.payload.get("finding_id", "").strip()
        if finding_id:
            set_experience_handoff_state(project_name, finding_id, "resolved")
        archive_agent_thread(project_name, approval.source_thread_id)
        outcome_payload = {
            "outcome_kind": "scope_confirmed",
            "outcome_title": approval.title,
            "outcome_reference_id": approval.approval_id,
            "outcome_detail": "Confirmed out of scope and resolved without creating new backlog work.",
        }
    else:
        raise ValueError(f"Unsupported approval type: {approval.approval_type}")

    updated_items = _load_approvals()
    updated_matching = next(
        (
            item
            for item in updated_items
            if str(item.get("approval_id", "")) == approval_id and str(item.get("project_name", "")) == project_name
        ),
        None,
    )
    if updated_matching is None:
        updated_matching = matching
        updated_items.append(updated_matching)
    updated_matching["status"] = "APPROVED"
    updated_matching["resolved_at"] = datetime.now(timezone.utc).isoformat()
    updated_matching["payload"] = {
        **{str(key): str(value) for key, value in approval.payload.items()},
        **outcome_payload,
    }
    _save_approvals(updated_items)
    return _approval_from_dict(updated_matching)


def reject_request(project_name: str, approval_id: str) -> ApprovalRequest:
    raw_items = _load_approvals()
    matching = next(
        (
            item
            for item in raw_items
            if str(item.get("approval_id", "")) == approval_id and str(item.get("project_name", "")) == project_name
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Approval not found: {approval_id}")
    if str(matching.get("status", "")) != "OPEN":
        raise ValueError(f"Approval is not open: {approval_id}")
    approval = _approval_from_dict(matching)
    outcome_payload: dict[str, str] = {}
    if approval.approval_type == "scope_confirmation":
        title = approval.payload.get("requirement_title", "").strip() or approval.title.strip()
        body = approval.payload.get("requirement_body", "").strip() or approval.summary.strip()
        record = append_requirement(
            project_name,
            title,
            body,
            status="BACKLOG",
            priority=approval.payload.get("priority", "MEDIUM"),
            effort=approval.payload.get("effort", "M"),
        )
        finding_id = approval.payload.get("finding_id", "").strip()
        if finding_id:
            set_experience_handoff_state(project_name, finding_id, "resolved")
        archive_agent_thread(project_name, approval.source_thread_id)
        outcome_payload = {
            "outcome_kind": "requirement",
            "outcome_title": record.title,
            "outcome_reference_id": record.id,
            "outcome_detail": f"Sent to backlog as {record.id} after rejecting the out-of-scope recommendation.",
        }
    matching["status"] = "REJECTED"
    matching["resolved_at"] = datetime.now(timezone.utc).isoformat()
    matching["payload"] = {
        **{str(key): str(value) for key, value in approval.payload.items()},
        **outcome_payload,
    }
    _save_approvals(raw_items)
    return _approval_from_dict(matching)


def workflow_inbox_items(project_name: str | None = None) -> list[InboxItem]:
    project_names: list[str]
    if project_name is not None:
        project_names = [project_name]
    else:
        project_names = [project.name for project in summarize_projects()]

    items: list[InboxItem] = []
    for current_project in project_names:
        for approval in active_approvals(current_project):
            items.append(
                InboxItem(
                    kind="approval",
                    title=approval.title,
                    summary=approval.summary,
                    project_name=current_project,
                    status_bucket="waiting",
                    reference_id=approval.approval_id,
                    detail=f"{approval.source_agent_name} approval request",
                )
            )

        for clarification in active_pm_clarifications(current_project):
            title = (
                f"{clarification.requirement_id} needs clarification"
                if clarification.requirement_id
                else f"{clarification.requirement_title or 'PM discovery'} needs clarification"
            )
            items.append(
                InboxItem(
                    kind="pm_clarification",
                    title=title,
                    summary=clarification.summary,
                    project_name=current_project,
                    status_bucket="blocked",
                    reference_id=clarification.clarification_id,
                    detail="Open PM clarification",
                )
            )

        for thread in list_agent_threads(current_project):
            if thread.status != "active":
                continue
            last_role = thread.messages[-1].role if thread.messages else ""
            if last_role == "assistant":
                items.append(
                    InboxItem(
                        kind="agent_thread",
                        title=f"{thread.agent_name} — {thread.mode}",
                        summary="Waiting on your reply in the live agent thread.",
                        project_name=current_project,
                        status_bucket="waiting",
                        reference_id=thread.thread_id,
                        detail=thread.messages[-1].content if thread.messages else "",
                    )
                )

        for finding in list_experience_findings(current_project):
            if finding.handoff_state in {"routed", "ready_for_pm_review", "ready_for_product_director", "handoff_prepared"}:
                items.append(
                    InboxItem(
                        kind="experience_finding",
                        title=f"Experience finding {finding.finding_id}",
                        summary=finding.user_problem,
                        project_name=current_project,
                        status_bucket="routed",
                        reference_id=finding.finding_id,
                        detail=f"{finding.handoff_state} -> {finding.recommended_next_role}",
                    )
                )

        for run in list_implementation_runs(current_project):
            if run.status in IMPLEMENTATION_ACTIVE_STATES:
                items.append(
                    InboxItem(
                        kind="implementation_run",
                        title=f"{run.requirement_id} implementation",
                        summary=run.summary or implementation_progress_message(run.status),
                        project_name=current_project,
                        status_bucket="running",
                        reference_id=run.run_id,
                        detail=run.status,
                    )
                )

    return items


def orchestrator_recommendation(project_name: str) -> OrchestratorRecommendation:
    project_dir = REPO_ROOT / "projects" / project_name
    requirements = parse_requirements(project_dir / "product" / "requirements.md")
    tasks = parse_tasks(project_dir / "product" / "tasks.md")
    findings = load_active_experience_findings(project_dir / "data" / "experience_findings.json")
    clarifications = load_active_pm_clarifications(project_dir / "data" / "pm_clarifications.json")
    agent_threads = load_active_agent_threads(project_dir / "data" / "agent_threads.json")
    approvals = active_approvals(project_name)

    if approvals:
        first = approvals[0]
        return OrchestratorRecommendation(
            next_action=f"Review approval request: {first.title}.",
            next_role="Product Director",
            why=f"{first.source_agent_name} created an open approval request that should be resolved before the workflow progresses.",
        )

    if clarifications:
        first = clarifications[0]
        target = first.get("requirement_id") or first.get("requirement_title") or "PM discovery"
        return OrchestratorRecommendation(
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
            return OrchestratorRecommendation(
                next_action=f"Continue the active {agent_name} {mode} thread in the project UI.",
                next_role="Product Director",
                why=f"Thread {thread['thread_id']} is still active and currently waiting on a human reply before the workflow can progress.",
            )
        return OrchestratorRecommendation(
            next_action=f"Continue the active {agent_name} {mode} thread.",
            next_role=agent_name or "PM",
            why=f"Thread {thread['thread_id']} is still active and should complete before the project is treated as idle.",
        )

    new_requirements = [item for item in requirements if item["status"] == "NEW"]
    if new_requirements:
        item = new_requirements[0]
        return OrchestratorRecommendation(
            next_action=f"Run PM on {item['id']}.",
            next_role="PM",
            why=f"{item['id']} is marked NEW in product/requirements.md and has not yet been turned into tasks.",
        )

    if findings:
        routed = next((item for item in findings if item["handoff_state"] == "routed"), None)
        if routed is not None:
            role = str(routed.get("recommended_next_role", "")) or "PM"
            return OrchestratorRecommendation(
                next_action=f"Run {role} on the routed workflow artifact.",
                next_role=role,
                why=f"Finding {routed['finding_id']} is routed and points to {role}.",
            )

        ready_pm = next((item for item in findings if item["handoff_state"] == "ready_for_pm_review"), None)
        if ready_pm is not None:
            return OrchestratorRecommendation(
                next_action="Run PM on the ready-for-review experience finding.",
                next_role="PM",
                why=f"Finding {ready_pm['finding_id']} is waiting on PM review.",
            )

        ready_pd = next((item for item in findings if item["handoff_state"] == "ready_for_product_director"), None)
        if ready_pd is not None:
            return OrchestratorRecommendation(
                next_action="Review the scope-escalation finding with the Product Director.",
                next_role="Product Director",
                why=f"Finding {ready_pd['finding_id']} is waiting on Product Director review.",
            )

    pending_tasks = [item for item in tasks if item["status"] in {"TODO", "IN_PROGRESS"}]
    if pending_tasks:
        first = pending_tasks[0]
        requirement_by_id = {item["id"]: item for item in requirements}
        linked_requirements = [requirement_by_id[req_id] for req_id in first.get("requirements", []) if req_id in requirement_by_id]
        if any(requirement_has_structural_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorRecommendation(
                next_action=f"Run Architect review before implementation on {linked_ids}.",
                next_role="Architect",
                why=f"{first['id']} is pending, but its linked requirement introduces a structural trigger that should be reviewed before Engineer starts.",
            )
        if any(requirement_has_experience_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorRecommendation(
                next_action=f"Run Experience Designer before implementation on {linked_ids}.",
                next_role="Experience Designer",
                why=f"{first['id']} is pending, and its linked requirement is experience-heavy enough that usability/workflow review should happen before Engineer starts.",
            )
        if any(requirement_has_ui_trigger(item) for item in linked_requirements):
            linked_ids = ", ".join(item["id"] for item in linked_requirements) or "the active requirement"
            return OrchestratorRecommendation(
                next_action=f"Run UI Designer before implementation on {linked_ids}.",
                next_role="UI Designer",
                why=f"{first['id']} is pending, and its linked requirement is UI-heavy enough that design direction or UI review should happen before Engineer starts.",
            )
        return OrchestratorRecommendation(
            next_action=f"Run Engineer on {first['id']}.",
            next_role="Engineer",
            why=f"{first['id']} is still {first['status']} in product/tasks.md.",
        )

    backlog = [item for item in requirements if item["status"] == "BACKLOG"]
    if backlog:
        return OrchestratorRecommendation(
            next_action="No agent needs to run automatically.",
            next_role="None",
            why="There are no NEW requirements, no active workflow artifacts, and no pending tasks. Remaining work is backlog only.",
        )

    return OrchestratorRecommendation(
        next_action="No agent needs to run automatically.",
        next_role="None",
        why="There are no NEW requirements, no active workflow artifacts, and no pending tasks.",
    )


def sprint_preimplementation_gate(project_name: str, requirement_id: str) -> tuple[str, str] | None:
    requirements = parse_requirements(_requirements_path(project_name))
    tasks = parse_tasks(_tasks_path(project_name))
    requirement_by_id = {item["id"]: item for item in requirements}
    requirement = requirement_by_id.get(requirement_id)
    if requirement is None:
        return None

    linked_pending_tasks = [
        task
        for task in tasks
        if task["status"] in {"TODO", "IN_PROGRESS"} and requirement_id in task.get("requirements", [])
    ]
    if not linked_pending_tasks:
        return None

    if requirement_has_structural_trigger(requirement):
        return (
            "Architect",
            f"{requirement_id} has pending task work and introduces structural change, so Architect should review it before implementation continues.",
        )
    if requirement_has_experience_trigger(requirement):
        return (
            "Experience Designer",
            f"{requirement_id} has pending task work and is experience-heavy enough that usability/workflow review should happen before implementation continues.",
        )
    if requirement_has_ui_trigger(requirement):
        return (
            "UI Designer",
            f"{requirement_id} has pending task work and is UI-heavy enough that design review should happen before implementation continues.",
        )
    return None


def list_pm_clarifications(project_name: str) -> list[PMClarification]:
    raw_items = _load_pm_clarifications(project_name)
    return [
        PMClarification(
            clarification_id=str(item["clarification_id"]),
            project_name=str(item["project_name"]),
            requirement_id=str(item["requirement_id"]),
            requirement_title=str(item.get("requirement_title", "")),
            source_thread_id=str(item.get("source_thread_id", "")),
            summary=str(item.get("summary", "")),
            questions=tuple(str(question) for question in item.get("questions", [])),
            status=str(item.get("status", "")),
            created_at=str(item.get("created_at", "")),
            resolved_at=str(item.get("resolved_at", "")),
        )
        for item in sorted(raw_items, key=lambda candidate: str(candidate.get("created_at", "")), reverse=True)
    ]


def active_pm_clarifications(project_name: str) -> list[PMClarification]:
    return [item for item in list_pm_clarifications(project_name) if item.status == "OPEN"]


def active_requirement_clarifications(project_name: str, requirement_id: str) -> list[PMClarification]:
    return [
        item
        for item in active_pm_clarifications(project_name)
        if item.requirement_id == requirement_id
    ]


def save_pm_clarification(
    project_name: str,
    *,
    requirement_id: str,
    requirement_title: str,
    source_thread_id: str = "",
    summary: str,
    questions: list[str],
) -> PMClarification:
    clarification = create_pm_clarification(
        _pm_clarifications_path(project_name),
        project_name=project_name,
        requirement_id=requirement_id,
        requirement_title=requirement_title,
        source_thread_id=source_thread_id,
        summary=summary,
        questions=questions,
    )
    return PMClarification(
        clarification_id=str(clarification["clarification_id"]),
        project_name=str(clarification["project_name"]),
        requirement_id=str(clarification["requirement_id"]),
        requirement_title=str(clarification["requirement_title"]),
        source_thread_id=str(clarification.get("source_thread_id", "")),
        summary=str(clarification["summary"]),
        questions=tuple(str(question) for question in clarification["questions"]),
        status=str(clarification["status"]),
        created_at=str(clarification["created_at"]),
        resolved_at=str(clarification.get("resolved_at", "")),
    )


def resolve_pm_clarification(project_name: str, clarification_id: str) -> PMClarification:
    matching = _resolve_pm_clarification_raw(project_name, clarification_id)
    return PMClarification(
        clarification_id=str(matching["clarification_id"]),
        project_name=str(matching["project_name"]),
        requirement_id=str(matching["requirement_id"]),
        requirement_title=str(matching.get("requirement_title", "")),
        source_thread_id=str(matching.get("source_thread_id", "")),
        summary=str(matching.get("summary", "")),
        questions=tuple(str(question) for question in matching.get("questions", [])),
        status=str(matching.get("status", "")),
        created_at=str(matching.get("created_at", "")),
        resolved_at=str(matching.get("resolved_at", "")),
    )


def answer_pm_clarification(project_name: str, clarification_id: str, reply: str) -> PMClarification:
    clarifications = _load_pm_clarifications(project_name)
    matching = next(
        (item for item in clarifications if str(item.get("clarification_id", "")) == clarification_id),
        None,
    )
    if matching is None:
        raise ValueError(f"PM clarification not found: {clarification_id}")

    source_thread_id = str(matching.get("source_thread_id", "")).strip()
    if not source_thread_id:
        return resolve_pm_clarification(project_name, clarification_id)

    raw_threads = _load_agent_threads()
    thread = next(
        (
            item
            for item in raw_threads
            if str(item.get("project_name", "")) == project_name
            and str(item.get("thread_id", "")) == source_thread_id
            and str(item.get("agent_name", "")) == "PM"
            and str(item.get("mode", "")) == "Requirement Discovery"
        ),
        None,
    )
    if thread is None:
        raise ValueError(f"Linked PM thread not found for clarification: {clarification_id}")

    thread.setdefault("messages", [])
    thread["messages"].append(_agent_message("user", reply))
    thread["status"] = "active"
    turn = _run_live_pm_turn(project_name, project_name, _agent_thread_messages(thread))
    _resolve_pm_clarification_raw(project_name, clarification_id)
    _apply_live_pm_turn_to_thread(project_name, thread, turn)
    thread["updated_at"] = datetime.now(timezone.utc).isoformat()
    _save_agent_threads(raw_threads)
    return resolve_pm_clarification(project_name, clarification_id)


def list_experience_findings(project_name: str) -> list[ExperienceFinding]:
    raw_findings = _load_experience_findings()
    project_findings = [finding for finding in raw_findings if finding.get("project_name") == project_name]
    return [
        ExperienceFinding(
            finding_id=str(finding["finding_id"]),
            project_name=str(finding["project_name"]),
            user_problem=str(finding["user_problem"]),
            affected_workflow=str(finding["affected_workflow"]),
            evidence=str(finding["evidence"]),
            confidence=str(finding["confidence"]),
            severity=str(finding["severity"]),
            frequency=str(finding["frequency"]),
            recommendation_type=str(finding["recommendation_type"]),
            rationale=str(finding["rationale"]),
            recommended_next_role=str(finding["recommended_next_role"]),
            handoff_state=str(finding["handoff_state"]),
            created_at=str(finding["created_at"]),
        )
        for finding in sorted(project_findings, key=lambda item: str(item["created_at"]), reverse=True)
    ]


def list_implementation_runs(project_name: str | None = None) -> list[ImplementationRun]:
    raw_runs = _load_implementation_runs()
    filtered_runs = raw_runs
    if project_name is not None:
        filtered_runs = [run for run in raw_runs if run.get("project_name") == project_name]
    return [
        _implementation_run_from_dict(run)
        for run in sorted(filtered_runs, key=lambda item: str(item.get("created_at", "")), reverse=True)
    ]


def _read_text_excerpt(path_str: str, *, max_chars: int = 2400, tail_lines: int | None = None) -> str:
    if not path_str:
        return ""
    path = Path(path_str)
    if not path.exists() or not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return ""
    if tail_lines is not None:
        lines = text.splitlines()
        text = "\n".join(lines[-tail_lines:])
    if len(text) <= max_chars:
        return text
    return "...\n" + text[-max_chars:]


def implementation_run_inspection(run: ImplementationRun) -> ImplementationRunInspection:
    if run.status in IMPLEMENTATION_ACTIVE_STATES:
        tone: Literal["active", "completed", "failed", "stale"] = "active"
        display_status = run.status.title()
    elif run.status == "COMPLETED":
        tone = "completed"
        display_status = "Completed"
    elif IMPLEMENTATION_STALE_ERROR_FRAGMENT in run.error:
        tone = "stale"
        display_status = "Failed (stale worker)"
    else:
        tone = "failed"
        display_status = "Failed"

    output_excerpt = _read_text_excerpt(run.output_path, max_chars=2000)
    log_excerpt = _read_text_excerpt(run.log_path, max_chars=2400, tail_lines=40)
    return ImplementationRunInspection(
        run=run,
        display_status=display_status,
        tone=tone,
        output_available=bool(run.output_path and Path(run.output_path).exists()),
        log_available=bool(run.log_path and Path(run.log_path).exists()),
        output_excerpt=output_excerpt,
        log_excerpt=log_excerpt,
    )


def recent_implementation_run_inspections(
    project_name: str,
    *,
    limit: int = 8,
) -> list[ImplementationRunInspection]:
    runs = list_implementation_runs(project_name)
    return [implementation_run_inspection(run) for run in runs[:limit]]


def _timeline_message_snippet(thread: AgentThread) -> str:
    latest_assistant = next((message for message in reversed(thread.messages) if message.role == "assistant"), None)
    if latest_assistant is not None and latest_assistant.content.strip():
        return latest_assistant.content.strip()
    if thread.draft_title.strip():
        return thread.draft_title.strip()
    if thread.idea.strip():
        return thread.idea.strip()
    return f"{thread.agent_name} {thread.mode} thread."


def _thread_timeline_event(thread: AgentThread) -> WorkflowTimelineEvent:
    status_bucket_map = {
        "active": "waiting",
        "blocked_clarification": "blocked",
        "pending_approval": "approval",
        "drafted": "recorded",
        "saved": "completed",
        "archived": "completed",
    }
    summary_map = {
        "active": "Thread is active and waiting on the next turn.",
        "blocked_clarification": "Thread is blocked on a PM clarification before it can continue.",
        "pending_approval": "Draft is waiting for approval before the workflow can continue.",
        "drafted": "Draft is ready for review in the agent workspace.",
        "saved": "Thread outcome has been saved into a durable project artifact.",
        "archived": "Thread has been archived after its downstream workflow completed.",
    }
    status_bucket = status_bucket_map.get(thread.status, "recorded")
    summary = summary_map.get(thread.status, _timeline_message_snippet(thread))
    detail = _timeline_message_snippet(thread)
    if thread.draft_title.strip() and detail != thread.draft_title.strip():
        detail = f"{thread.draft_title.strip()}\n\n{detail}"
    return WorkflowTimelineEvent(
        event_id=f"thread:{thread.thread_id}:{thread.updated_at or thread.created_at}",
        project_name=thread.project_name,
        occurred_at=thread.updated_at or thread.created_at,
        title=f"{thread.agent_name} · {thread.mode}",
        summary=summary,
        actor=thread.agent_name,
        artifact_kind="agent thread",
        artifact_id=thread.thread_id,
        status_bucket=status_bucket,
        detail=detail,
    )


def _approval_created_event(approval: ApprovalRequest) -> WorkflowTimelineEvent:
    return WorkflowTimelineEvent(
        event_id=f"approval-created:{approval.approval_id}",
        project_name=approval.project_name,
        occurred_at=approval.created_at,
        title=approval.title,
        summary=approval.summary,
        actor=approval.source_agent_name,
        artifact_kind="approval",
        artifact_id=approval.approval_id,
        status_bucket="approval",
        detail=f"{approval.approval_type.replace('_', ' ')} requested by {approval.source_agent_name}.",
    )


def _approval_resolved_event(approval: ApprovalRequest) -> WorkflowTimelineEvent | None:
    if not approval.resolved_at:
        return None
    outcome_detail = approval.payload.get("outcome_detail", "").strip()
    outcome_title = approval.payload.get("outcome_title", "").strip()
    outcome_reference = approval.payload.get("outcome_reference_id", "").strip()
    detail_parts = [part for part in [outcome_detail, outcome_title, outcome_reference] if part]
    return WorkflowTimelineEvent(
        event_id=f"approval-resolved:{approval.approval_id}",
        project_name=approval.project_name,
        occurred_at=approval.resolved_at,
        title=f"{approval.title} — {approval.status.title()}",
        summary=outcome_detail or f"Approval was {approval.status.lower()}.",
        actor="Product Director",
        artifact_kind="approval outcome",
        artifact_id=approval.approval_id,
        status_bucket="completed",
        detail=" · ".join(detail_parts),
    )


def _clarification_created_event(clarification: PMClarification) -> WorkflowTimelineEvent:
    return WorkflowTimelineEvent(
        event_id=f"clarification-created:{clarification.clarification_id}",
        project_name=clarification.project_name,
        occurred_at=clarification.created_at,
        title=f"PM clarification · {clarification.requirement_id}",
        summary=clarification.summary,
        actor="PM",
        artifact_kind="clarification",
        artifact_id=clarification.clarification_id,
        status_bucket="blocked",
        detail="\n".join(clarification.questions),
    )


def _clarification_resolved_event(clarification: PMClarification) -> WorkflowTimelineEvent | None:
    if clarification.status != "RESOLVED":
        return None
    occurred_at = clarification.resolved_at or clarification.created_at
    return WorkflowTimelineEvent(
        event_id=f"clarification-resolved:{clarification.clarification_id}",
        project_name=clarification.project_name,
        occurred_at=occurred_at,
        title=f"PM clarification resolved · {clarification.requirement_id}",
        summary="Clarification was answered and the blocked workflow could continue.",
        actor="Product Director",
        artifact_kind="clarification",
        artifact_id=clarification.clarification_id,
        status_bucket="completed",
        detail=clarification.summary,
    )


def _experience_finding_event(finding: ExperienceFinding) -> WorkflowTimelineEvent:
    active_states = {"ready_for_pm_review", "ready_for_product_director", "handoff_prepared", "routed"}
    status_bucket = "routed" if finding.handoff_state in active_states else "completed"
    return WorkflowTimelineEvent(
        event_id=f"finding:{finding.finding_id}:{finding.created_at}",
        project_name=finding.project_name,
        occurred_at=finding.created_at,
        title="Experience finding saved",
        summary=finding.user_problem,
        actor="Experience Designer",
        artifact_kind="experience finding",
        artifact_id=finding.finding_id,
        status_bucket=status_bucket,
        detail=f"{finding.handoff_state} -> {finding.recommended_next_role}",
    )


def _implementation_run_events(run: ImplementationRun) -> list[WorkflowTimelineEvent]:
    inspected = implementation_run_inspection(run)
    events = [
        WorkflowTimelineEvent(
            event_id=f"run-created:{run.run_id}",
            project_name=run.project_name,
            occurred_at=run.created_at,
            title=f"Implementation queued · {run.requirement_id}",
            summary=f"{run.requirement_title}",
            actor="Engineer",
            artifact_kind="implementation run",
            artifact_id=run.run_id,
            status_bucket="running" if run.status in IMPLEMENTATION_ACTIVE_STATES else "recorded",
            detail=f"Run created for {run.requirement_id}.",
        )
    ]
    if run.finished_at:
        events.append(
            WorkflowTimelineEvent(
                event_id=f"run-finished:{run.run_id}",
                project_name=run.project_name,
                occurred_at=run.finished_at,
                title=f"Implementation {inspected.display_status.lower()} · {run.requirement_id}",
                summary=run.summary or run.error or implementation_progress_message(run.status),
                actor="Engineer",
                artifact_kind="implementation run",
                artifact_id=run.run_id,
                status_bucket="completed" if inspected.tone == "completed" else "blocked",
                detail=f"{run.requirement_title}",
            )
        )
    return events


def workflow_timeline_events(project_name: str, *, limit: int = 16) -> list[WorkflowTimelineEvent]:
    events: list[WorkflowTimelineEvent] = []

    events.extend(_thread_timeline_event(thread) for thread in list_agent_threads(project_name))
    for approval in list_approvals(project_name):
        events.append(_approval_created_event(approval))
        resolved = _approval_resolved_event(approval)
        if resolved is not None:
            events.append(resolved)
    for clarification in list_pm_clarifications(project_name):
        events.append(_clarification_created_event(clarification))
        resolved = _clarification_resolved_event(clarification)
        if resolved is not None:
            events.append(resolved)
    events.extend(_experience_finding_event(finding) for finding in list_experience_findings(project_name))
    for run in list_implementation_runs(project_name):
        events.extend(_implementation_run_events(run))

    ordered = sorted(events, key=lambda item: item.occurred_at, reverse=True)
    return ordered[:limit]


def _worker_process_alive(worker_pid: int | None) -> bool:
    if worker_pid is None or worker_pid <= 0:
        return False
    try:
        os.kill(worker_pid, 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        return False
    return True


def _iso_age_minutes(value: str) -> float | None:
    if not value:
        return None
    try:
        created = datetime.fromisoformat(value)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - created).total_seconds() / 60.0


def reconcile_implementation_runs(project_name: str | None = None) -> list[ImplementationRun]:
    raw_runs = _load_implementation_runs()
    now = datetime.now(timezone.utc).isoformat()
    changed = False
    for run in raw_runs:
        if project_name is not None and run.get("project_name") != project_name:
            continue
        status = str(run.get("status", "")).upper()
        if status not in IMPLEMENTATION_ACTIVE_STATES:
            continue

        worker_pid = run.get("worker_pid")
        if worker_pid is not None:
            try:
                worker_pid = int(worker_pid)
            except (TypeError, ValueError):
                worker_pid = None

        age_minutes = _iso_age_minutes(str(run.get("started_at") or run.get("created_at") or ""))
        alive = _worker_process_alive(worker_pid)
        if alive:
            continue

        if worker_pid is None and (age_minutes is None or age_minutes < IMPLEMENTATION_STALE_MINUTES):
            continue

        run["status"] = "FAILED"
        run["finished_at"] = now
        run["error"] = (
            "Implementation worker is no longer running, so this run was marked failed during reconciliation."
        )
        changed = True

    if changed:
        _save_implementation_runs(raw_runs)

    return list_implementation_runs(project_name)


def active_implementation_run(project_name: str | None = None) -> ImplementationRun | None:
    reconcile_implementation_runs(project_name)
    return next(
        (
            run
            for run in list_implementation_runs(project_name)
            if run.status in IMPLEMENTATION_ACTIVE_STATES
        ),
        None,
    )


def latest_requirement_implementation(project_name: str, requirement_id: str) -> ImplementationRun | None:
    reconcile_implementation_runs(project_name)
    return next(
        (
            run
            for run in list_implementation_runs(project_name)
            if run.requirement_id == requirement_id
        ),
        None,
    )


def plan_sprint_requirement(project_name: str, requirement_id: str) -> SprintPlan:
    requirement_map = _requirement_by_id(project_name)
    record = requirement_map.get(requirement_id)
    if record is None:
        raise ValueError(f"Requirement not found: {requirement_id}")
    if record.status != "BACKLOG":
        raise ValueError(f"Only backlog requirements can be added to a sprint: {requirement_id}")

    existing = load_sprint_plan(project_name)
    if existing is not None and existing.status in {"ACTIVE", "BLOCKED"}:
        raise ValueError("Cannot change the sprint plan while a sprint is active or blocked.")

    created_at = existing.created_at if existing is not None else datetime.now(timezone.utc).isoformat()
    requirement_ids = tuple(existing.requirement_ids) if existing is not None else ()
    if requirement_id in requirement_ids:
        return existing

    return _replace_sprint_plan(
        project_name,
        status="PLANNING",
        requirement_ids=(*requirement_ids, requirement_id),
        created_at=created_at,
        started_at="",
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )


def remove_sprint_requirement(project_name: str, requirement_id: str) -> SprintPlan | None:
    existing = load_sprint_plan(project_name)
    if existing is None:
        return None
    if existing.status in {"ACTIVE", "BLOCKED"}:
        raise ValueError("Cannot change the sprint plan while a sprint is active or blocked.")

    remaining = tuple(item for item in existing.requirement_ids if item != requirement_id)
    if not remaining:
        _save_sprint_plan_raw(project_name, None)
        return None

    return _replace_sprint_plan(
        project_name,
        status="PLANNING",
        requirement_ids=remaining,
        created_at=existing.created_at,
        started_at="",
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )


def move_sprint_requirement(project_name: str, requirement_id: str, delta: int) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None:
        raise ValueError("No sprint plan exists for this project.")
    if existing.status in {"ACTIVE", "BLOCKED"}:
        raise ValueError("Cannot reorder the sprint plan while a sprint is active or blocked.")
    if requirement_id not in existing.requirement_ids:
        raise ValueError(f"Requirement not found in sprint: {requirement_id}")

    ids = list(existing.requirement_ids)
    current_index = ids.index(requirement_id)
    target_index = current_index + delta
    if target_index < 0 or target_index >= len(ids):
        return existing

    ids[current_index], ids[target_index] = ids[target_index], ids[current_index]
    return _replace_sprint_plan(
        project_name,
        status="PLANNING",
        requirement_ids=tuple(ids),
        created_at=existing.created_at,
        started_at="",
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )


def _clear_sprint_if_empty(project_name: str, plan: SprintPlan) -> SprintPlan | None:
    if plan.requirement_ids:
        return plan
    _save_sprint_plan_raw(project_name, None)
    return None


def _blocked_sprint(plan: SprintPlan, requirement_id: str, reason: str) -> SprintPlan:
    return _replace_sprint_plan(
        plan.project_name,
        status="BLOCKED",
        requirement_ids=plan.requirement_ids,
        created_at=plan.created_at,
        started_at=plan.started_at,
        completed_at="",
        current_requirement_id=requirement_id,
        blocked_reason=reason,
    )


def complete_sprint(project_name: str) -> None:
    existing = load_sprint_plan(project_name)
    if existing is None:
        raise ValueError("No sprint exists for this project.")
    if existing.status != "READY_TO_CLOSE":
        raise ValueError("Sprint is not ready for completion confirmation.")
    _replace_sprint_plan(
        project_name,
        status="COMPLETED",
        requirement_ids=(),
        created_at=existing.created_at,
        started_at=existing.started_at,
        completed_at=existing.completed_at or datetime.now(timezone.utc).isoformat(),
        current_requirement_id="",
        blocked_reason="",
    )


def advance_active_sprint(project_name: str) -> SprintPlan | None:
    plan = load_sprint_plan(project_name)
    if plan is None or plan.status != "ACTIVE":
        return plan

    requirement_map = _requirement_by_id(project_name)
    valid_requirement_ids = tuple(item for item in plan.requirement_ids if item in requirement_map)
    if valid_requirement_ids != plan.requirement_ids:
        plan = _replace_sprint_plan(
            project_name,
            status=plan.status,
            requirement_ids=valid_requirement_ids,
            created_at=plan.created_at,
            started_at=plan.started_at,
            completed_at=plan.completed_at,
            current_requirement_id=plan.current_requirement_id,
            blocked_reason=plan.blocked_reason,
        )
        if plan is None:
            return None

    active_run = active_implementation_run(project_name)
    if active_run is not None:
        return _replace_sprint_plan(
            project_name,
            status="ACTIVE",
            requirement_ids=plan.requirement_ids,
            created_at=plan.created_at,
            started_at=plan.started_at,
            completed_at="",
            current_requirement_id=active_run.requirement_id,
            blocked_reason="",
        )

    for requirement_id in plan.requirement_ids:
        record = requirement_map.get(requirement_id)
        if record is None:
            continue
        if record.status == "DONE":
            continue

        latest_run = latest_requirement_implementation(project_name, requirement_id)
        was_backlog = record.status == "BACKLOG"
        if was_backlog:
            record = RequirementRecord(
                id=record.id,
                title=record.title,
                status="NEW",
                priority=record.priority,
                effort=record.effort,
                description=record.description,
            )
            update_requirement(project_name, record)
            requirement_map[requirement_id] = record

        if not was_backlog and latest_run is not None and latest_run.status in {"FAILED", "COMPLETED"}:
            reason = (
                latest_run.error.strip()
                or latest_run.summary.strip()
                or "This sprint requirement needs attention before the sprint can continue."
            )
            return _blocked_sprint(plan, requirement_id, reason)

        if not implementation_entry_allowed(record):
            return _blocked_sprint(
                plan,
                requirement_id,
                "This requirement is no longer eligible for implementation from the sprint flow.",
            )

        gate = sprint_preimplementation_gate(project_name, requirement_id)
        if gate is not None:
            role, reason = gate
            return _blocked_sprint(
                plan,
                requirement_id,
                f"Sprint paused for {role}: {reason}",
            )

        run = start_requirement_implementation(project_name, record)
        return _replace_sprint_plan(
            project_name,
            status="ACTIVE",
            requirement_ids=plan.requirement_ids,
            created_at=plan.created_at,
            started_at=plan.started_at,
            completed_at="",
            current_requirement_id=run.requirement_id,
            blocked_reason="",
        )

    return _replace_sprint_plan(
        project_name,
        status="READY_TO_CLOSE",
        requirement_ids=plan.requirement_ids,
        created_at=plan.created_at,
        started_at=plan.started_at,
        completed_at=datetime.now(timezone.utc).isoformat(),
        current_requirement_id="",
        blocked_reason="",
    )


def start_sprint(project_name: str) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None or not existing.requirement_ids:
        raise ValueError("Add at least one backlog requirement to the sprint before starting it.")
    if existing.status == "ACTIVE":
        return advance_active_sprint(project_name) or existing
    if active_implementation_run(project_name) is not None:
        raise RuntimeError("A requirement implementation run is already active in this project.")

    active_plan = _replace_sprint_plan(
        project_name,
        status="ACTIVE",
        requirement_ids=existing.requirement_ids,
        created_at=existing.created_at,
        started_at=existing.started_at or datetime.now(timezone.utc).isoformat(),
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )
    return advance_active_sprint(project_name) or active_plan


def continue_sprint(project_name: str) -> SprintPlan:
    existing = load_sprint_plan(project_name)
    if existing is None:
        raise ValueError("No sprint exists for this project.")
    if existing.status == "COMPLETED":
        return existing
    active_plan = _replace_sprint_plan(
        project_name,
        status="ACTIVE",
        requirement_ids=existing.requirement_ids,
        created_at=existing.created_at,
        started_at=existing.started_at or datetime.now(timezone.utc).isoformat(),
        completed_at="",
        current_requirement_id="",
        blocked_reason="",
    )
    return advance_active_sprint(project_name) or active_plan


def advance_all_active_sprints() -> None:
    for project_dir in iter_projects():
        plan = load_sprint_plan(project_dir.name)
        if plan is not None and plan.status == "ACTIVE":
            advance_active_sprint(project_dir.name)


def implementation_entry_allowed(record: RequirementRecord) -> bool:
    return record.status in {"NEW", "IN_PROGRESS"}


def implementation_progress_percent(status: str) -> int:
    return IMPLEMENTATION_PROGRESS_BY_STATUS.get(status.upper(), 0)


def implementation_progress_message(status: str) -> str:
    return IMPLEMENTATION_PROGRESS_MESSAGE_BY_STATUS.get(
        status.upper(),
        "Implementation status is being prepared.",
    )


def _project_path(project_name: str) -> Path:
    return REPO_ROOT / "projects" / project_name


def _sprint_path(project_name: str) -> Path:
    return _project_path(project_name) / "data" / "sprint.json"


def _load_sprint_plan_raw(project_name: str) -> dict[str, object] | None:
    path = _sprint_path(project_name)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        return None
    return data


def _save_sprint_plan_raw(project_name: str, payload: dict[str, object] | None) -> None:
    path = _sprint_path(project_name)
    if payload is None:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def _sprint_plan_from_dict(raw_plan: dict[str, object], project_name: str) -> SprintPlan:
    return SprintPlan(
        project_name=project_name,
        status=str(raw_plan.get("status", "PLANNING")),
        requirement_ids=tuple(str(item) for item in raw_plan.get("requirement_ids", []) if str(item).strip()),
        created_at=str(raw_plan.get("created_at", "")),
        started_at=str(raw_plan.get("started_at", "")),
        completed_at=str(raw_plan.get("completed_at", "")),
        current_requirement_id=str(raw_plan.get("current_requirement_id", "")),
        blocked_reason=str(raw_plan.get("blocked_reason", "")),
    )


def load_sprint_plan(project_name: str) -> SprintPlan | None:
    raw_plan = _load_sprint_plan_raw(project_name)
    if raw_plan is None:
        return None
    return _sprint_plan_from_dict(raw_plan, project_name)


def _persist_sprint_plan(plan: SprintPlan | None) -> SprintPlan | None:
    if plan is None:
        return None
    _save_sprint_plan_raw(
        plan.project_name,
        {
            "status": plan.status,
            "requirement_ids": list(plan.requirement_ids),
            "created_at": plan.created_at,
            "started_at": plan.started_at,
            "completed_at": plan.completed_at,
            "current_requirement_id": plan.current_requirement_id,
            "blocked_reason": plan.blocked_reason,
        },
    )
    return plan


def _replace_sprint_plan(
    project_name: str,
    *,
    status: str,
    requirement_ids: tuple[str, ...],
    created_at: str,
    started_at: str,
    completed_at: str,
    current_requirement_id: str,
    blocked_reason: str,
) -> SprintPlan:
    return _persist_sprint_plan(
        SprintPlan(
            project_name=project_name,
            status=status,
            requirement_ids=requirement_ids,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            current_requirement_id=current_requirement_id,
            blocked_reason=blocked_reason,
        )
    )


def _requirement_by_id(project_name: str) -> dict[str, RequirementRecord]:
    document = load_requirement_document(project_name)
    return {
        record.id: record
        for record in (document.active_requirements + document.backlog_requirements)
    }


def sprint_requirement_records(project_name: str) -> tuple[RequirementRecord, ...]:
    plan = load_sprint_plan(project_name)
    if plan is None:
        return ()
    requirement_map = _requirement_by_id(project_name)
    return tuple(
        requirement_map[requirement_id]
        for requirement_id in plan.requirement_ids
        if requirement_id in requirement_map
    )


def _preview_port(project_name: str) -> int:
    digest = hashlib.sha1(project_name.encode("utf-8")).hexdigest()
    return PREVIEW_PORT_BASE + (int(digest[:8], 16) % PREVIEW_PORT_SPAN)


def _streamlit_preview_command(entry_path: Path, port: int) -> tuple[str, ...]:
    return (
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(entry_path),
        "--server.headless",
        "true",
        "--server.port",
        str(port),
        "--browser.gatherUsageStats",
        "false",
    )


def project_preview(project_name: str) -> ProjectPreview:
    project_dir = _project_path(project_name)
    streamlit_entry = project_dir / "src" / "app.py"
    if streamlit_entry.exists():
        port = _preview_port(project_name)
        return ProjectPreview(
            project_name=project_name,
            available=True,
            runtime="streamlit",
            entry_path=streamlit_entry,
            url=f"http://localhost:{port}",
            command=_streamlit_preview_command(streamlit_entry, port),
            status_text="Streamlit project preview is available.",
        )

    return ProjectPreview(
        project_name=project_name,
        available=False,
        runtime="unavailable",
        entry_path=None,
        url="",
        command=(),
        status_text="Preview is unavailable because this project does not expose src/app.py.",
    )


def _local_port_accepts_connections(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _listener_pids(port: int) -> tuple[int, ...]:
    result = subprocess.run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        return ()
    pids: list[int] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            pids.append(int(line))
        except ValueError:
            continue
    return tuple(dict.fromkeys(pids))


def _process_command(pid: int) -> str:
    result = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _is_managed_preview_command(command: str) -> bool:
    return "-m streamlit run" in command and "/projects/" in command and "/src/app.py" in command


def _preview_process_matches(preview: ProjectPreview) -> bool:
    if not preview.available:
        return False
    entry_path = str(preview.entry_path)
    for pid in _listener_pids(_preview_port(preview.project_name)):
        command = _process_command(pid)
        if entry_path in command:
            return True
    return False


def _terminate_preview_processes(port: int) -> None:
    for pid in _listener_pids(port):
        command = _process_command(pid)
        if not _is_managed_preview_command(command):
            continue
        try:
            os.kill(pid, 15)
        except ProcessLookupError:
            continue


def project_preview_running(project_name: str) -> bool:
    preview = project_preview(project_name)
    if not preview.available:
        return False
    port = _preview_port(project_name)
    if not _local_port_accepts_connections(port):
        return False
    return _preview_process_matches(preview)


def start_project_preview(project_name: str) -> ProjectPreview:
    preview = project_preview(project_name)
    if not preview.available:
        raise ValueError(preview.status_text)

    port = _preview_port(project_name)
    if _local_port_accepts_connections(port):
        if _preview_process_matches(preview):
            return preview
        _terminate_preview_processes(port)

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "").strip()
    repo_pythonpath = str(REPO_ROOT)
    if existing_pythonpath:
        if repo_pythonpath not in existing_pythonpath.split(os.pathsep):
            env["PYTHONPATH"] = f"{repo_pythonpath}{os.pathsep}{existing_pythonpath}"
    else:
        env["PYTHONPATH"] = repo_pythonpath

    subprocess.Popen(
        preview.command,
        cwd=str(_project_path(project_name)),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    return preview


def _archive_active_agent_threads(
    project_name: str,
    raw_threads: list[dict[str, object]],
    *,
    agent_name: str,
    mode: str,
) -> None:
    for thread in raw_threads:
        if (
            thread.get("project_name") == project_name
            and thread.get("agent_name") == agent_name
            and thread.get("mode") == mode
            and thread.get("status") == "active"
        ):
            thread["status"] = "archived"
            thread["updated_at"] = datetime.now(timezone.utc).isoformat()


def _experience_next_role(recommendation_type: str) -> str:
    if recommendation_type == "scope escalation":
        return "Product Director"
    return "PM"


def _experience_handoff_state(recommendation_type: str) -> str:
    if recommendation_type == "scope escalation":
        return "ready_for_product_director"
    return "ready_for_pm_review"


def save_experience_finding(
    project_name: str,
    *,
    user_problem: str,
    affected_workflow: str,
    evidence: str,
    confidence: str,
    severity: str,
    frequency: str,
    recommendation_type: str,
    rationale: str,
) -> ExperienceFinding:
    raw_findings = _load_experience_findings()
    finding = {
        "finding_id": str(uuid4()),
        "project_name": project_name,
        "user_problem": user_problem.strip(),
        "affected_workflow": affected_workflow.strip(),
        "evidence": evidence.strip(),
        "confidence": confidence.strip(),
        "severity": severity.strip(),
        "frequency": frequency.strip(),
        "recommendation_type": recommendation_type.strip(),
        "rationale": rationale.strip(),
        "recommended_next_role": _experience_next_role(recommendation_type.strip()),
        "handoff_state": _experience_handoff_state(recommendation_type.strip()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    raw_findings.append(finding)
    _save_experience_findings(raw_findings)
    return ExperienceFinding(
        finding_id=str(finding["finding_id"]),
        project_name=str(finding["project_name"]),
        user_problem=str(finding["user_problem"]),
        affected_workflow=str(finding["affected_workflow"]),
        evidence=str(finding["evidence"]),
        confidence=str(finding["confidence"]),
        severity=str(finding["severity"]),
        frequency=str(finding["frequency"]),
        recommendation_type=str(finding["recommendation_type"]),
        rationale=str(finding["rationale"]),
        recommended_next_role=str(finding["recommended_next_role"]),
        handoff_state=str(finding["handoff_state"]),
        created_at=str(finding["created_at"]),
    )


def _resolve_codex_executable() -> Path:
    candidates = [Path.home() / ".codex" / "bin" / "codex"]
    candidates.extend(
        sorted(
            (Path.home() / ".vscode" / "extensions").glob("openai.chatgpt-*/bin/macos-aarch64/codex"),
            reverse=True,
        )
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Could not find a local Codex executable for implementation runs.")


def build_requirement_implementation_prompt(project_name: str, requirement_id: str) -> str:
    requirement = next(
        (
            item
            for item in parse_requirements(_requirements_path(project_name))
            if item["id"] == requirement_id
        ),
        None,
    )
    extra_guidance: list[str] = []
    if requirement is not None:
        if requirement_has_experience_trigger(requirement):
            extra_guidance.append(
                "This requirement is experience-related. Do not skip Experience Designer; use it to shape usability/workflow requirements before Engineer implementation."
            )
        if requirement_has_ui_trigger(requirement):
            extra_guidance.append(
                "This requirement is UI-related. Do not skip UI Designer; use it to shape design requirements, UI constraints, or design-brief-driven follow-up work before Engineer implementation."
            )
    return "\n".join(
        [
            f"You are continuing AI Builder OS workflow for project `{project_name}` and requirement `{requirement_id}`.",
            "Use the deterministic helper `python tools/orchestrator_status.py "
            f"{project_name}` as the routing source of truth before acting.",
            "Then execute the full OS workflow needed for this requirement without waiting for handoff approval unless genuinely blocked.",
            *extra_guidance,
            "Stay within the project scope, update file-backed state as work progresses, run relevant validation, and close requirement/task state when appropriate.",
            "Your final response must include:",
            "- what changed",
            "- validation results",
            "- whether the requirement is now done or still blocked",
            "- any error or follow-up needed",
        ]
    )


def _implementation_worker_script() -> Path:
    return REPO_ROOT / "projects" / "os-control-panel" / "tools" / "run_requirement_implementation.py"


def _implementation_command(run_id: str, project_name: str, requirement_id: str) -> list[str]:
    return [
        str(REPO_ROOT / ".venv" / "bin" / "python"),
        str(_implementation_worker_script()),
        "--run-id",
        run_id,
        "--project-name",
        project_name,
        "--requirement-id",
        requirement_id,
    ]


def update_implementation_run(
    run_id: str,
    *,
    status: str | None = None,
    summary: str | None = None,
    error: str | None = None,
    created_at: str | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
    output_path: str | None = None,
    log_path: str | None = None,
    worker_pid: int | None = None,
) -> ImplementationRun:
    raw_runs = _load_implementation_runs()
    matching = next((run for run in raw_runs if run.get("run_id") == run_id), None)
    if matching is None:
        raise ValueError(f"Implementation run not found: {run_id}")

    if status is not None:
        matching["status"] = status
    if summary is not None:
        matching["summary"] = summary
    if error is not None:
        matching["error"] = error
    if created_at is not None:
        matching["created_at"] = created_at
    if started_at is not None:
        matching["started_at"] = started_at
    if finished_at is not None:
        matching["finished_at"] = finished_at
    if output_path is not None:
        matching["output_path"] = output_path
    if log_path is not None:
        matching["log_path"] = log_path
    if worker_pid is not None:
        matching["worker_pid"] = worker_pid

    _save_implementation_runs(raw_runs)
    return _implementation_run_from_dict(matching)


def start_requirement_implementation(project_name: str, record: RequirementRecord) -> ImplementationRun:
    active_run = active_implementation_run(project_name)
    if active_run is not None:
        raise RuntimeError(
            f"Implementation is already active for {active_run.project_name} {active_run.requirement_id}."
        )

    if not implementation_entry_allowed(record):
        raise ValueError(f"{record.id} is not eligible for UI-initiated implementation.")

    run_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    output_path = IMPLEMENTATION_LOG_DIR / f"{run_id}-last-message.txt"
    log_path = IMPLEMENTATION_LOG_DIR / f"{run_id}.log"
    raw_runs = _load_implementation_runs()
    raw_run = {
        "run_id": run_id,
        "project_name": project_name,
        "requirement_id": record.id,
        "requirement_title": record.title,
        "status": "QUEUED",
        "summary": "",
        "error": "",
        "created_at": created_at,
        "started_at": "",
        "finished_at": "",
        "output_path": str(output_path),
        "log_path": str(log_path),
        "worker_pid": None,
    }
    raw_runs.append(raw_run)
    _save_implementation_runs(raw_runs)

    command = _implementation_command(run_id, project_name, record.id)
    try:
        with log_path.open("ab") as log_handle:
            process = subprocess.Popen(
                command,
                cwd=REPO_ROOT,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
    except Exception as exc:
        return update_implementation_run(run_id, status="FAILED", error=str(exc), finished_at=datetime.now(timezone.utc).isoformat())

    return update_implementation_run(run_id, worker_pid=process.pid)


def set_experience_handoff_state(project_name: str, finding_id: str, handoff_state: str) -> ExperienceFinding:
    normalized_state = handoff_state.strip()
    if normalized_state not in EXPERIENCE_HANDOFF_STATES:
        raise ValueError(f"Invalid experience handoff state: {handoff_state}")

    raw_findings = _load_experience_findings()
    matching = next(
        (
            finding
            for finding in raw_findings
            if finding.get("project_name") == project_name and finding.get("finding_id") == finding_id
        ),
        None,
    )
    if matching is None:
        raise ValueError(f"Experience finding not found: {finding_id}")

    matching["handoff_state"] = normalized_state
    _save_experience_findings(raw_findings)
    return ExperienceFinding(
        finding_id=str(matching["finding_id"]),
        project_name=str(matching["project_name"]),
        user_problem=str(matching["user_problem"]),
        affected_workflow=str(matching["affected_workflow"]),
        evidence=str(matching["evidence"]),
        confidence=str(matching["confidence"]),
        severity=str(matching["severity"]),
        frequency=str(matching["frequency"]),
        recommendation_type=str(matching["recommendation_type"]),
        rationale=str(matching["rationale"]),
        recommended_next_role=str(matching["recommended_next_role"]),
        handoff_state=str(matching["handoff_state"]),
        created_at=str(matching["created_at"]),
    )


def build_discovery_draft(project_name: str, idea: str, answers: dict[str, str]) -> str:
    current_requirements = parse_requirements(_requirements_path(project_name))
    existing_titles = ", ".join(requirement["id"] for requirement in current_requirements) or "none yet"

    def answer(key: str, fallback: str) -> str:
        value = answers.get(key, "").strip()
        return value or fallback

    return "\n".join(
        [
            "Problem statement",
            f"- {answer('problem', idea.strip() or 'Clarify the primary problem this project should solve.')}",
            "",
            "Target user",
            f"- {answer('target_user', 'Clarify the primary user for this idea.')}",
            "",
            "Core job-to-be-done",
            f"- {answer('context', 'Clarify the current workflow or context this idea should improve.')}",
            "",
            "Success criteria",
            f"- {answer('success', 'Define what success looks like for the first version.')}",
            "",
            "Constraints",
            f"- {answer('constraints', 'Clarify the constraints or guardrails for the first version.')}",
            "",
            "Out of scope",
            f"- {answer('out_of_scope', 'Clarify what should not be included in the first version.')}",
            "",
            "Assumptions",
            f"- Existing requirement IDs in this project: {existing_titles}",
            f"- Initial idea entered: {idea.strip() or 'No initial idea was provided.'}",
            "",
            "Open questions",
            "- Which parts of this draft should become a new requirement versus a refinement of existing requirements?",
        ]
    )


def summarize_projects() -> list[ProjectSummary]:
    summaries: list[ProjectSummary] = []
    for project_dir in iter_projects():
        missing_paths = tuple(validate_project_structure(project_dir))
        requirements = parse_requirements(project_dir / "product" / "requirements.md")
        tasks = parse_tasks(project_dir / "product" / "tasks.md")

        requirement_counts: dict[str, int] = {}
        for requirement in requirements:
            status = requirement["status"]
            requirement_counts[status] = requirement_counts.get(status, 0) + 1

        task_counts: dict[str, int] = {}
        for task in tasks:
            status = task["status"]
            task_counts[status] = task_counts.get(status, 0) + 1

        new_requirements = tuple(
            RequirementSummary(
                id=requirement["id"],
                title=requirement["title"],
                status=requirement["status"],
            )
            for requirement in requirements
            if requirement["status"] == "NEW"
        )

        pending_tasks = tuple(
            TaskSummary(
                id=task["id"],
                title=task["title"],
                status=task["status"],
            )
            for task in tasks
            if task["status"] != "DONE"
        )

        summaries.append(
            ProjectSummary(
                name=project_dir.name,
                path=project_dir,
                structure_ok=not missing_paths,
                missing_paths=missing_paths,
                requirement_counts=requirement_counts,
                new_requirements=new_requirements,
                task_counts=task_counts,
                pending_tasks=pending_tasks,
            )
        )

    return summaries


def workspace_totals(projects: list[ProjectSummary]) -> dict[str, int]:
    totals = {
        "projects": len(projects),
        "new_requirements": 0,
        "pending_tasks": 0,
    }
    for project in projects:
        totals["new_requirements"] += len(project.new_requirements)
        totals["pending_tasks"] += len(project.pending_tasks)
    return totals
