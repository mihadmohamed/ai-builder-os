from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PMMode = Literal["discovery", "requirement_draft", "prioritisation", "task_plan"]
PMDecisionStatus = Literal["NEEDS_INPUT", "READY_FOR_APPROVAL"]
PMOperationalMode = Literal["prioritisation", "task_plan"]
PMNextAction = Literal[
    "ask_question",
    "request_clarification",
    "draft_requirement",
    "prioritise_requirements",
    "plan_tasks",
]


class PMContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PMSourceState(PMContractModel):
    requirements_sha256: str = ""
    tasks_sha256: str = ""
    memory_sha256: str = ""
    history_event_id: str = ""


class PMWorkRequestPayload(PMContractModel):
    schema_version: Literal["2026-07-18.pm-work.v1"] = "2026-07-18.pm-work.v1"
    mode: PMOperationalMode
    target_requirement_ids: list[str] = Field(default_factory=list)
    operator_context: str = Field(default="", max_length=4_000)
    parent_proposal_id: str = ""
    parent_proposal_revision: int = 0

    @model_validator(mode="after")
    def validate_shape(self) -> "PMWorkRequestPayload":
        normalized = [value.strip() for value in self.target_requirement_ids]
        if any(not value for value in normalized):
            raise ValueError("PM work-request requirement IDs must not be empty")
        if len(normalized) != len(set(normalized)):
            raise ValueError("PM work-request requirement IDs must be unique")
        if self.mode == "prioritisation" and len(normalized) < 2:
            raise ValueError("Prioritisation requires at least two target requirements")
        if self.mode == "task_plan" and len(normalized) != 1:
            raise ValueError("Task planning requires exactly one target requirement")
        has_parent_id = bool(self.parent_proposal_id.strip())
        has_parent_revision = self.parent_proposal_revision > 0
        if has_parent_id != has_parent_revision:
            raise ValueError("Parent proposal ID and revision must be provided together")
        self.target_requirement_ids = normalized
        return self


class PMSpecialistConsultation(PMContractModel):
    role: Literal["Architect", "Engineer", "QA", "Experience Designer", "UI Designer"]
    question: str
    finding: str


class PMClarification(PMContractModel):
    summary: str = ""
    questions: list[str] = Field(default_factory=list)


class PMRequirementChange(PMContractModel):
    action: Literal["create", "update"] = "create"
    requirement_id: str = ""
    title: str
    status: Literal["NEW", "BACKLOG", "IN_PROGRESS"] = "NEW"
    priority: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    effort: Literal["S", "M", "L", "XL"] = "M"
    description: str
    ui_runtime: str = ""


class PMTaskChange(PMContractModel):
    action: Literal["create", "update"] = "create"
    task_number: int = 0
    title: str
    task_type: Literal["Feature Task", "Validation Task"] = "Feature Task"
    status: Literal["TODO"] = "TODO"
    requirement_ids: list[str] = Field(default_factory=list)
    goal: str
    requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    validation: list[str] = Field(default_factory=list)


class PMPrioritisation(PMContractModel):
    selected_requirement_id: str = ""
    deferred_requirement_ids: list[str] = Field(default_factory=list)
    rationale: str = ""
    strategy_alignment: Literal["continues", "changes", "not_applicable"] = "not_applicable"
    evidence_basis: str = ""


class PMDecisionEnvelope(PMContractModel):
    schema_version: Literal["2026-07-18.pm.v1"] = "2026-07-18.pm.v1"
    proposal_id: str = ""
    proposal_revision: int = 0
    project_name: str = ""
    mode: PMMode
    status: PMDecisionStatus
    next_action: PMNextAction
    assistant_message: str
    work_request: PMWorkRequestPayload | None = None
    source_state: PMSourceState = Field(default_factory=PMSourceState)
    facts: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    rationale: str = ""
    consultations: list[PMSpecialistConsultation] = Field(default_factory=list)
    clarification: PMClarification = Field(default_factory=PMClarification)
    requirement_changes: list[PMRequirementChange] = Field(default_factory=list)
    task_changes: list[PMTaskChange] = Field(default_factory=list)
    prioritisation: PMPrioritisation = Field(default_factory=PMPrioritisation)
    durable_intents: list[str] = Field(default_factory=list)
    approval_summary: str = ""

    def has_canonical_changes(self) -> bool:
        return bool(self.requirement_changes or self.task_changes or self.durable_intents)
