from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


PMMode = Literal[
    "discovery",
    "requirement_draft",
    "prioritisation",
    "task_plan",
    "artifact_review",
    "outcome_review",
]
PMDecisionStatus = Literal["NEEDS_INPUT", "READY_FOR_APPROVAL"]
PMOperationalMode = Literal["prioritisation", "task_plan", "artifact_review", "outcome_review"]
PMNextAction = Literal[
    "ask_question",
    "request_clarification",
    "draft_requirement",
    "prioritise_requirements",
    "plan_tasks",
    "review_artifact",
    "review_outcome",
]
PMEvidenceSourceKind = Literal[
    "product_history",
    "implementation",
    "qa",
    "release",
    "customer_feedback",
    "analytics",
    "experiment",
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
    authorization_proposal_id: str = ""
    authorization_proposal_revision: int = 0

    @model_validator(mode="after")
    def validate_shape(self) -> "PMWorkRequestPayload":
        normalized = [value.strip() for value in self.target_requirement_ids]
        if any(not value for value in normalized):
            raise ValueError("PM work-request requirement IDs must not be empty")
        if len(normalized) != len(set(normalized)):
            raise ValueError("PM work-request requirement IDs must be unique")
        if self.mode == "prioritisation" and not normalized:
            raise ValueError("Prioritisation requires at least one target requirement")
        if self.mode == "task_plan" and len(normalized) != 1:
            raise ValueError("Task planning requires exactly one target requirement")
        if self.mode in {"artifact_review", "outcome_review"} and len(normalized) != 1:
            raise ValueError(f"{self.mode} requires exactly one target requirement or artifact")
        has_parent_id = bool(self.parent_proposal_id.strip())
        has_parent_revision = self.parent_proposal_revision > 0
        if has_parent_id != has_parent_revision:
            raise ValueError("Parent proposal ID and revision must be provided together")
        has_authorization_id = bool(self.authorization_proposal_id.strip())
        has_authorization_revision = self.authorization_proposal_revision > 0
        if has_authorization_id != has_authorization_revision:
            raise ValueError("Authorization proposal ID and revision must be provided together")
        if has_authorization_id and self.mode != "task_plan":
            raise ValueError("Only derived task planning may carry requirement authorization")
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


class PMEvidenceReference(PMContractModel):
    evidence_type: Literal[
        "artifact",
        "requirement_intent",
        "task",
        "implementation",
        "qa",
        "release",
        "outcome_signal",
        "prior_decision",
        "missing",
    ]
    source_id: str
    title: str
    status: str = ""
    occurred_at: str = ""
    summary: str
    available: bool = True
    provenance: str = ""
    confidence: Literal["", "low", "medium", "high", "unknown"] = ""
    stale: bool = False


PMLearningReviewState = Literal[
    "not_yet_due",
    "ready",
    "insufficient_evidence",
    "decision_pending",
    "reviewed",
]


class PMFirstPartyEvidenceSource(PMContractModel):
    kind: PMEvidenceSourceKind
    configured: bool
    available: bool
    source_id: str
    owner: str = ""
    privacy_boundary: str = ""
    references: list[dict[str, Any]] = Field(default_factory=list, max_length=50)
    unavailable_reason: str = ""


class PMModeEvidencePacket(PMContractModel):
    schema_version: Literal["2026-07-21.pm-evidence.v1"] = "2026-07-21.pm-evidence.v1"
    project_name: str
    mode: PMMode
    target_requirement_ids: list[str] = Field(default_factory=list)
    sources: list[PMFirstPartyEvidenceSource] = Field(default_factory=list, min_length=1)
    missing_sources: list[PMEvidenceSourceKind] = Field(default_factory=list)
    source_state: PMSourceState = Field(default_factory=PMSourceState)

    @model_validator(mode="after")
    def validate_sources(self) -> "PMModeEvidencePacket":
        kinds = [item.kind for item in self.sources]
        if len(kinds) != len(set(kinds)):
            raise ValueError("PM evidence packet source kinds must be unique")
        if self.missing_sources != [item.kind for item in self.sources if not item.available]:
            raise ValueError("PM evidence packet missing_sources must match unavailable sources")
        return self


class PMGuardrailFinding(PMContractModel):
    severity: Literal["info", "warning", "blocking"]
    code: str = Field(min_length=1, max_length=80)
    field: str = ""
    message: str = Field(min_length=1, max_length=1_000)
    remediation: str = Field(min_length=1, max_length=1_000)


class PMReviewEvidencePacket(PMContractModel):
    review_mode: Literal["artifact_review", "outcome_review"]
    target_id: str
    references: list[PMEvidenceReference] = Field(default_factory=list, max_length=50)
    missing_evidence: list[str] = Field(default_factory=list, max_length=20)
    consolidation_candidate_ids: list[str] = Field(default_factory=list, max_length=10)
    review_state: PMLearningReviewState | None = None
    review_window: str = ""
    review_due_at: str = ""
    expected_evidence: list[str] = Field(default_factory=list, max_length=20)
    evidence_provenance: list[str] = Field(default_factory=list, max_length=20)
    evidence_confidence: Literal["", "low", "medium", "high", "unknown"] = ""
    missing_sources: list[PMEvidenceSourceKind] = Field(default_factory=list)
    source_state: PMSourceState = Field(default_factory=PMSourceState)

    @model_validator(mode="after")
    def validate_packet(self) -> "PMReviewEvidencePacket":
        if not self.target_id.strip():
            raise ValueError("PM review evidence target_id must not be empty")
        identities = [
            (item.evidence_type, item.source_id.strip())
            for item in self.references
        ]
        if any(not source_id for _, source_id in identities):
            raise ValueError("PM evidence source IDs must not be empty")
        if len(identities) != len(set(identities)):
            raise ValueError("PM evidence references must be unique by type and source ID")
        if any(not item.title.strip() or not item.summary.strip() for item in self.references):
            raise ValueError("PM evidence references require a title and summary")
        if any(not value.strip() for value in self.missing_evidence):
            raise ValueError("PM missing-evidence descriptions must not be empty")
        if len(self.consolidation_candidate_ids) != len(set(self.consolidation_candidate_ids)):
            raise ValueError("PM consolidation candidates must be unique")
        if self.review_mode == "artifact_review" and self.review_state is not None:
            raise ValueError("Learning-loop review state is valid only for outcome review")
        if len(self.expected_evidence) != len(set(self.expected_evidence)):
            raise ValueError("Expected outcome evidence must be unique")
        if len(self.evidence_provenance) != len(set(self.evidence_provenance)):
            raise ValueError("Outcome evidence provenance must be unique")
        if len(self.missing_sources) != len(set(self.missing_sources)):
            raise ValueError("Outcome missing sources must be unique")
        return self


class PMArtifactReviewDecision(PMContractModel):
    action: Literal["none", "merge", "defer", "reject", "follow_up"] = "none"
    artifact_id: str = ""
    target_requirement_id: str = ""
    rationale: str = ""


class PMOutcomeReviewDecision(PMContractModel):
    action: Literal[
        "none",
        "accept",
        "close",
        "remediate",
        "follow_up_discovery",
        "follow_up_validation",
        "iterate",
        "experiment",
        "revise",
        "stop",
    ] = "none"
    requirement_id: str = ""
    rationale: str = ""
    evidence_limitation: str = ""
    follow_up_requirement_ids: list[str] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def validate_learning_decision(self) -> "PMOutcomeReviewDecision":
        normalized = [item.strip() for item in self.follow_up_requirement_ids]
        if any(not item or not item.removeprefix("R").isdigit() for item in normalized):
            raise ValueError("Outcome follow-up requirement IDs must be valid R-numbers")
        if len(normalized) != len(set(normalized)):
            raise ValueError("Outcome follow-up requirement IDs must be unique")
        self.follow_up_requirement_ids = normalized
        return self


class PMDecisionEnvelope(PMContractModel):
    schema_version: Literal["2026-07-18.pm.v1", "2026-07-19.pm.v2"] = "2026-07-19.pm.v2"
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
    review_evidence: PMReviewEvidencePacket | None = None
    artifact_review: PMArtifactReviewDecision = Field(default_factory=PMArtifactReviewDecision)
    outcome_review: PMOutcomeReviewDecision = Field(default_factory=PMOutcomeReviewDecision)
    durable_intents: list[str] = Field(default_factory=list)
    approval_summary: str = ""

    @model_validator(mode="after")
    def validate_review_shape(self) -> "PMDecisionEnvelope":
        if self.mode == "artifact_review":
            if self.review_evidence is not None and self.review_evidence.review_mode != self.mode:
                raise ValueError("Artifact review requires an artifact-review evidence packet")
            if self.status == "READY_FOR_APPROVAL" and self.artifact_review.action == "none":
                raise ValueError("Artifact review must select a typed action")
            if not self.artifact_review.artifact_id.strip():
                raise ValueError("Artifact review requires an artifact ID")
        elif self.artifact_review.action != "none":
            raise ValueError("Artifact-review decisions are valid only in artifact_review mode")

        if self.mode == "outcome_review":
            if self.review_evidence is not None and self.review_evidence.review_mode != self.mode:
                raise ValueError("Outcome review requires an outcome-review evidence packet")
            if self.status == "READY_FOR_APPROVAL" and self.outcome_review.action == "none":
                raise ValueError("Outcome review must select a typed action")
            if not self.outcome_review.requirement_id.strip():
                raise ValueError("Outcome review requires a requirement ID")
        elif self.outcome_review.action != "none":
            raise ValueError("Outcome-review decisions are valid only in outcome_review mode")
        return self

    def has_canonical_changes(self) -> bool:
        return bool(self.requirement_changes or self.task_changes or self.durable_intents)
