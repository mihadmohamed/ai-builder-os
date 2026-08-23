from __future__ import annotations

import json
import math
import re
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
from statistics import median
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from control_plane.storage import atomic_write_json, control_data_dir, load_json, project_lock, project_path, read_history, utc_now


SCHEMA_VERSION = "2026-08-23.system-learning.v1"
CODEX_TELEMETRY_COMPATIBILITY_VERSION = "2026-08-23.codex-native-telemetry.v1"
FAST_MINIMUM_SAMPLES = 5
SLOW_MINIMUM_SAMPLES = 20
SAFE_CODE_PREFIXES = ("projects/os-control-panel/src/", "agent/roles/", ".codex/agents/")
CAPABILITY_VERSION = "2026-08-23.r108.v1"
QUALITY_EVAL_VERSION = "2026-08-23.quality-eval.v1"
PM_QUALITY_COMPATIBILITY_VERSION = "2026-08-23.pm-operational-quality.v1"
BASELINE_METRIC_SEMANTICS_VERSION = "2026-08-23.efficiency-baseline.v2"
DIAGNOSIS_PRIORITY_THRESHOLD = 1.0
PM_CAPABILITY_MODES = ("discovery", "requirement_draft", "prioritisation", "task_plan", "artifact_review", "outcome_review")
CODEX_TELEMETRY_METRICS = (
    "model", "reasoning_effort", "input_tokens", "cached_input_tokens", "cache_write_tokens",
    "output_tokens", "reasoning_tokens", "model_requests", "tool_calls", "tool_result_size",
    "context.static_instructions", "context.project_context", "context.session_context",
    "context.tool_results", "retries", "quality_score", "eval_passed", "guardrail_passed",
    "outcome", "estimated_cost_usd", "pricing_provenance", "latency.agent_execution",
    "latency.controller", "latency.queue_wait", "latency.governance_wait",
    "latency.total_lifecycle",
)


class LearningModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ContextBreakdown(LearningModel):
    static_instructions: int = Field(default=0, ge=0)
    project_context: int = Field(default=0, ge=0)
    session_context: int = Field(default=0, ge=0)
    tool_results: int = Field(default=0, ge=0)
    unit: Literal["characters", "tokens"] = "characters"


class MetricEvidence(LearningModel):
    status: Literal["attributable", "derived", "unavailable"]
    source: str = ""
    unit: str = ""
    semantics: str = ""
    compatibility_version: str = CODEX_TELEMETRY_COMPATIBILITY_VERSION
    privacy_classification: Literal["operational_metadata", "aggregate_usage", "unavailable"]
    source_event_ids: list[str] = Field(default_factory=list)
    unavailable_reason: str = ""

    @model_validator(mode="after")
    def validate_evidence(self) -> "MetricEvidence":
        self.source_event_ids = sorted(set(item.strip() for item in self.source_event_ids if item.strip()))
        if self.status == "unavailable":
            if not self.unavailable_reason.strip():
                raise ValueError("Unavailable metric evidence requires a reason")
            if self.source_event_ids:
                raise ValueError("Unavailable metric evidence cannot claim source events")
        elif not self.source.strip() or not self.semantics.strip():
            raise ValueError("Available metric evidence requires source and semantics")
        return self


class LatencyBreakdown(LearningModel):
    agent_execution_seconds: float | None = Field(default=None, ge=0)
    controller_seconds: float | None = Field(default=None, ge=0)
    queue_wait_seconds: float | None = Field(default=None, ge=0)
    governance_wait_seconds: float | None = Field(default=None, ge=0)
    total_lifecycle_seconds: float | None = Field(default=None, ge=0)
    unavailable_phases: dict[str, str] = Field(default_factory=dict)
    boundary_provenance: str = ""

    @model_validator(mode="after")
    def validate_non_overlapping_phases(self) -> "LatencyBreakdown":
        known = (
            self.agent_execution_seconds, self.controller_seconds,
            self.queue_wait_seconds, self.governance_wait_seconds,
        )
        if self.total_lifecycle_seconds is not None:
            phase_total = sum(value for value in known if value is not None)
            if phase_total > self.total_lifecycle_seconds + 1e-6:
                raise ValueError("Latency phases cannot overlap or exceed total lifecycle time")
        return self


class TelemetrySourceAssessment(LearningModel):
    metric: str
    status: Literal["attributable", "derived", "unavailable"]
    source: str = ""
    unit: str = ""
    semantics: str = ""
    compatibility_version: str = CODEX_TELEMETRY_COMPATIBILITY_VERSION
    privacy_classification: Literal["operational_metadata", "aggregate_usage", "unavailable"]
    limitation: str = ""


class CodexTelemetryCapabilityReport(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    report_id: str
    workflow_mode: Literal["requirement_draft", "task_plan"]
    evidence_boundary: str = "canonical_product_history"
    assessments: list[TelemetrySourceAssessment]

    @model_validator(mode="after")
    def validate_complete_metric_inventory(self) -> "CodexTelemetryCapabilityReport":
        metrics = [item.metric for item in self.assessments]
        if len(metrics) != len(set(metrics)):
            raise ValueError("Telemetry metrics must be classified exactly once")
        if set(metrics) != set(CODEX_TELEMETRY_METRICS):
            raise ValueError("Telemetry capability report must classify every R110 metric")
        return self


class QualityDimensionDefinition(LearningModel):
    dimension: str
    weight: float = Field(gt=0, le=1)
    evidence: str
    r100_compatibility: Literal["compatible", "incompatible"]


class PMQualityProfile(LearningModel):
    profile_id: str
    profile_version: str = PM_QUALITY_COMPATIBILITY_VERSION
    compatibility_version: str = PM_QUALITY_COMPATIBILITY_VERSION
    workflow_mode: Literal["requirement_draft", "task_plan"]
    pass_threshold: float = Field(default=0.8, ge=0, le=1)
    minimum_complete_dimensions: int = Field(ge=1)
    dimensions: list[QualityDimensionDefinition] = Field(min_length=1)
    quality_guardrails: list[str] = Field(min_length=1)
    safety_guardrails: list[str] = Field(min_length=1)
    missing_evidence_behavior: Literal["unavailable"] = "unavailable"

    @model_validator(mode="after")
    def validate_profile(self) -> "PMQualityProfile":
        names = [item.dimension for item in self.dimensions]
        if len(names) != len(set(names)):
            raise ValueError("Quality profile dimensions must be unique")
        if abs(sum(item.weight for item in self.dimensions) - 1.0) > 1e-6:
            raise ValueError("Quality profile weights must sum to one")
        if self.minimum_complete_dimensions != len(self.dimensions):
            raise ValueError("Operational quality profiles fail closed unless every scored dimension is complete")
        return self


class QualitySourceAssessment(LearningModel):
    dimension: str
    status: Literal["attributable", "derived", "incompatible", "unavailable"]
    source: str = ""
    semantics: str
    privacy_classification: Literal["operational_metadata", "unavailable"]
    limitation: str = ""


class PMQualityCapabilityReport(LearningModel):
    report_id: str
    workflow_mode: Literal["requirement_draft", "task_plan"]
    profile_id: str
    compatibility_version: str = PM_QUALITY_COMPATIBILITY_VERSION
    assessments: list[QualitySourceAssessment]

    @model_validator(mode="after")
    def validate_unique_dimensions(self) -> "PMQualityCapabilityReport":
        names = [item.dimension for item in self.assessments]
        if len(names) != len(set(names)):
            raise ValueError("Quality sources must be classified exactly once")
        return self


class WorkflowQualityEvidence(LearningModel):
    status: Literal["attributable", "unavailable", "incompatible"]
    workflow_mode: Literal["requirement_draft", "task_plan"]
    profile_id: str
    profile_version: str
    compatibility_version: str
    artifact_id: str
    artifact_revision: int = Field(ge=1)
    artifact_fingerprint: str
    deterministic_input_fingerprint: str
    evaluated_at: str
    quality_score: float | None = Field(default=None, ge=0, le=1)
    eval_passed: bool | None = None
    guardrail_passed: bool | None = None
    dimension_scores: dict[str, float | None] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    unavailable_reason: str = ""
    evidence_provenance: str

    @model_validator(mode="after")
    def validate_evidence(self) -> "WorkflowQualityEvidence":
        complete = (self.quality_score, self.eval_passed, self.guardrail_passed)
        if self.status == "attributable":
            if any(value is None for value in complete):
                raise ValueError("Attributable quality evidence requires score, eval, and guardrail results")
            if self.unavailable_reason:
                raise ValueError("Attributable quality evidence cannot carry an unavailable reason")
        else:
            if any(value is not None for value in complete):
                raise ValueError("Unavailable quality evidence cannot carry score or pass results")
            if not self.unavailable_reason.strip():
                raise ValueError("Unavailable quality evidence requires a reason")
        return self


def pm_quality_profile(workflow_mode: str) -> PMQualityProfile:
    if workflow_mode not in {"requirement_draft", "task_plan"}:
        raise ValueError("Operational PM quality supports requirement_draft and task_plan")
    common = [
        QualityDimensionDefinition(
            dimension="typed_output_contract", weight=0.20,
            evidence="Exact controller-retained PMDecisionEnvelope validates for the declared mode and identity.",
            r100_compatibility="compatible",
        ),
        QualityDimensionDefinition(
            dimension="evidence_classification", weight=0.20,
            evidence="Facts, evidence, assumptions, source fingerprints, and conflicts are deterministically inspectable.",
            r100_compatibility="compatible",
        ),
    ]
    if workflow_mode == "requirement_draft":
        dimensions = common + [
            QualityDimensionDefinition(
                dimension="acceptance_testability", weight=0.35,
                evidence="Every proposed requirement contains the canonical sections and observable acceptance bullets.",
                r100_compatibility="compatible",
            ),
            QualityDimensionDefinition(
                dimension="deterministic_guardrails", weight=0.25,
                evidence="The artifact is decision-ready, conflict-free, and contains a reviewable approval boundary.",
                r100_compatibility="compatible",
            ),
        ]
    else:
        dimensions = common + [
            QualityDimensionDefinition(
                dimension="task_verifiability", weight=0.25,
                evidence="Every task has a substantive goal, requirements, constraints, and validation evidence.",
                r100_compatibility="compatible",
            ),
            QualityDimensionDefinition(
                dimension="authorization_lineage", weight=0.20,
                evidence="The typed task-plan work request carries an exact approved requirement authorization.",
                r100_compatibility="compatible",
            ),
            QualityDimensionDefinition(
                dimension="deterministic_guardrails", weight=0.15,
                evidence="The artifact is decision-ready, conflict-free, and contains a bounded auto-application summary.",
                r100_compatibility="compatible",
            ),
        ]
    return PMQualityProfile(
        profile_id=f"{QUALITY_EVAL_VERSION}.pm.{workflow_mode}",
        workflow_mode=workflow_mode,
        minimum_complete_dimensions=len(dimensions),
        dimensions=dimensions,
        quality_guardrails=[
            "Every scored dimension is complete.",
            "The weighted score meets the versioned pass threshold.",
        ],
        safety_guardrails=[
            "No blocking ambiguity or fact/assumption conflict is present.",
            "Task plans preserve exact approved requirement authorization.",
            "Approval status alone contributes no score.",
        ],
    )


def codex_native_quality_capability_report(workflow_mode: str) -> PMQualityCapabilityReport:
    profile = pm_quality_profile(workflow_mode)
    assessments = [
        QualitySourceAssessment(
            dimension=item.dimension,
            status="attributable" if item.dimension == "typed_output_contract" else "derived",
            source="controller_pm_proposal_record",
            semantics=item.evidence,
            privacy_classification="operational_metadata",
        )
        for item in profile.dimensions
    ]
    assessments.extend([
        QualitySourceAssessment(
            dimension="tool_choice", status="unavailable", semantics="R100 tool-choice grading requires a model/tool trace.",
            privacy_classification="unavailable", limitation="Codex-native canonical lifecycle and proposal records contain no complete model-visible tool trajectory.",
        ),
        QualitySourceAssessment(
            dimension="specialist_and_trajectory_judgment", status="incompatible",
            semantics="R100 specialist selection and trajectory grading is case-specific and trace-dependent.",
            privacy_classification="unavailable", limitation="Operational proposal structure cannot substitute for case expectations or a retained trace.",
        ),
        QualitySourceAssessment(
            dimension="subjective_product_strategy", status="unavailable",
            semantics="Strategic judgment remains a human product decision rather than a deterministic structural score.",
            privacy_classification="unavailable", limitation="No deterministic source can responsibly score subjective strategy.",
        ),
    ])
    return PMQualityCapabilityReport(
        report_id=_stable_id("pm-quality-report", PM_QUALITY_COMPATIBILITY_VERSION, workflow_mode),
        workflow_mode=workflow_mode,
        profile_id=profile.profile_id,
        assessments=assessments,
    )


def _quality_fingerprint(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")).hexdigest()


def evaluate_pm_quality_artifact(
    project_name: str,
    artifact: dict[str, Any] | None,
    *,
    workflow_mode: str,
    proposal_id: str,
    proposal_revision: int,
) -> WorkflowQualityEvidence:
    """Score only deterministic structure in one exact controller-retained PM artifact."""
    from pm_contract import PMDecisionEnvelope

    profile = pm_quality_profile(workflow_mode)
    raw = dict(artifact or {})
    payload = raw.get("proposal") if isinstance(raw.get("proposal"), dict) else None
    evaluated_at = str(raw.get("submitted_at") or "unavailable")
    identity = {
        "project_name": project_name,
        "proposal_id": proposal_id,
        "proposal_revision": proposal_revision,
        "workflow_mode": workflow_mode,
    }
    artifact_fingerprint = _quality_fingerprint(payload or identity)

    def unavailable(reason: str, *, status: Literal["unavailable", "incompatible"] = "unavailable") -> WorkflowQualityEvidence:
        return WorkflowQualityEvidence(
            status=status,
            workflow_mode=workflow_mode,  # type: ignore[arg-type]
            profile_id=profile.profile_id,
            profile_version=profile.profile_version,
            compatibility_version=profile.compatibility_version,
            artifact_id=proposal_id,
            artifact_revision=proposal_revision,
            artifact_fingerprint=artifact_fingerprint,
            deterministic_input_fingerprint=_quality_fingerprint({**identity, "artifact": artifact_fingerprint}),
            evaluated_at=evaluated_at,
            dimension_scores={item.dimension: None for item in profile.dimensions},
            unavailable_reason=reason,
            evidence_provenance="Exact project-scoped PM proposal store lookup; no history summary or approval inference.",
        )

    if payload is None:
        return unavailable("The exact retained PM proposal artifact is unavailable; lifecycle summaries are insufficient.")
    if (
        str(raw.get("project_name", "")) != project_name
        or str(raw.get("proposal_id", "")) != proposal_id
        or int(raw.get("proposal_revision", 0) or 0) != proposal_revision
    ):
        return unavailable("The retained artifact identity does not match the exact project, proposal, and revision.", status="incompatible")
    try:
        decision = PMDecisionEnvelope.model_validate(payload)
    except Exception:
        return unavailable("The exact retained artifact does not validate against the versioned PM decision contract.", status="incompatible")
    if decision.project_name != project_name or decision.mode != workflow_mode:
        return unavailable("The retained artifact mode or project is incompatible with this observation.", status="incompatible")

    findings: list[str] = []
    scores: dict[str, float | None] = {}
    contract_ok = (
        decision.proposal_id == proposal_id
        and decision.proposal_revision == proposal_revision
        and decision.status == "READY_FOR_APPROVAL"
        and decision.has_canonical_changes()
    )
    scores["typed_output_contract"] = 1.0 if contract_ok else 0.0
    if not contract_ok:
        findings.append("typed_output_contract_failed")

    source_state = decision.source_state
    source_complete = all((
        source_state.requirements_sha256,
        source_state.tasks_sha256,
        source_state.memory_sha256,
    ))
    normalized_assumptions = {item.strip().casefold() for item in decision.assumptions if item.strip()}
    fact_conflict = any(item.strip().casefold() in normalized_assumptions for item in decision.facts)
    evidence_ok = source_complete and (not decision.facts or bool(decision.evidence)) and not fact_conflict
    scores["evidence_classification"] = 1.0 if evidence_ok else 0.0
    if not evidence_ok:
        findings.append("evidence_classification_failed")

    if workflow_mode == "requirement_draft":
        required_sections = (
            "Problem statement", "Target user", "Core job-to-be-done", "Desired outcome",
            "Success and acceptance evidence", "Constraints", "Out of scope", "Assumptions", "Open questions",
        )
        acceptance_ok = bool(decision.requirement_changes) and all(
            all(f"{section}:" in change.description for section in required_sections)
            and bool(re.search(r"Success and acceptance evidence:\s*.*?(?m:^\s*-\s+\S+)", change.description, re.S))
            for change in decision.requirement_changes
        )
        scores["acceptance_testability"] = 1.0 if acceptance_ok else 0.0
        if not acceptance_ok:
            findings.append("acceptance_testability_failed")
    else:
        task_ok = bool(decision.task_changes) and all(
            len(task.goal.strip()) >= 15
            and bool(task.requirement_ids)
            and bool(task.requirements)
            and bool(task.constraints)
            and bool(task.validation)
            and all(len(item.strip()) >= 8 for item in task.validation)
            for task in decision.task_changes
        )
        scores["task_verifiability"] = 1.0 if task_ok else 0.0
        if not task_ok:
            findings.append("task_verifiability_failed")
        request = decision.work_request
        authorization_ok = bool(
            request
            and request.mode == "task_plan"
            and len(request.target_requirement_ids) == 1
            and request.authorization_proposal_id
            and request.authorization_proposal_revision > 0
        )
        scores["authorization_lineage"] = 1.0 if authorization_ok else 0.0
        if not authorization_ok:
            findings.append("authorization_lineage_failed")

    guardrail_ok = bool(decision.approval_summary.strip()) and not fact_conflict and not any(
        item.strip().casefold().startswith("blocking:") for item in decision.open_questions
    )
    scores["deterministic_guardrails"] = 1.0 if guardrail_ok else 0.0
    if not guardrail_ok:
        findings.append("deterministic_guardrails_failed")
    if set(scores) != {item.dimension for item in profile.dimensions}:
        return unavailable("The evaluator could not produce every required profile dimension.")
    score = sum(scores[item.dimension] * item.weight for item in profile.dimensions if scores[item.dimension] is not None)
    guardrail_passed = guardrail_ok and not fact_conflict and (
        workflow_mode != "task_plan" or scores.get("authorization_lineage") == 1.0
    )
    eval_passed = score >= profile.pass_threshold and guardrail_passed
    return WorkflowQualityEvidence(
        status="attributable",
        workflow_mode=workflow_mode,  # type: ignore[arg-type]
        profile_id=profile.profile_id,
        profile_version=profile.profile_version,
        compatibility_version=profile.compatibility_version,
        artifact_id=proposal_id,
        artifact_revision=proposal_revision,
        artifact_fingerprint=artifact_fingerprint,
        deterministic_input_fingerprint=_quality_fingerprint({
            **identity, "artifact": artifact_fingerprint, "profile": profile.model_dump(mode="json"),
        }),
        evaluated_at=evaluated_at,
        quality_score=round(score, 6),
        eval_passed=eval_passed,
        guardrail_passed=guardrail_passed,
        dimension_scores=scores,
        findings=sorted(findings),
        evidence_provenance=(
            "Exact immutable PM proposal artifact evaluated against deterministic structural dimensions; "
            "approval status, tool trajectory, and subjective strategy contribute no score."
        ),
    )


class CapabilityDescriptor(LearningModel):
    capability_id: str = Field(pattern=r"^[a-z0-9]+(?:[._-][a-z0-9]+)*$")
    capability_version: str = Field(min_length=1)
    role: str = Field(min_length=1)
    workflow_mode: str = Field(min_length=1)
    telemetry_contract_version: str = Field(min_length=1)
    quality_eval_profile: str = ""
    change_marker: str = Field(min_length=1)
    eligibility: Literal["eligible", "not_applicable"] = "eligible"
    not_applicable_rationale: str = ""

    @model_validator(mode="after")
    def validate_eligibility(self) -> "CapabilityDescriptor":
        self.not_applicable_rationale = " ".join(self.not_applicable_rationale.split()).strip()
        if self.eligibility == "eligible":
            if not self.quality_eval_profile.strip():
                raise ValueError("Eligible capabilities require a quality-eval profile")
            if self.not_applicable_rationale:
                raise ValueError("Eligible capabilities cannot carry a not-applicable rationale")
        elif not self.not_applicable_rationale:
            raise ValueError("Not-applicable capabilities require a rationale")
        return self


class CapabilityRegistry(LearningModel):
    descriptors: list[CapabilityDescriptor] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_identities(self) -> "CapabilityRegistry":
        identities = [(item.capability_id, item.capability_version) for item in self.descriptors]
        routes = [(item.role, item.workflow_mode) for item in self.descriptors]
        if len(identities) != len(set(identities)):
            raise ValueError("Capability identities must be unique")
        if len(routes) != len(set(routes)):
            raise ValueError("Capability role and mode routes must be unique")
        return self

    def resolve(self, role: str, workflow_mode: str) -> CapabilityDescriptor:
        for descriptor in self.descriptors:
            if descriptor.role == role and descriptor.workflow_mode == workflow_mode:
                return descriptor
        raise ValueError(f"Unregistered model-backed capability: {role}/{workflow_mode}")


def _capability_slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    return normalized or "unknown"


def _default_capability_descriptors() -> list[CapabilityDescriptor]:
    roles = (
        "Orchestrator", "Experience Designer", "UI Designer", "Architect", "Engineer", "QA",
        "Learning Agent", "OS Learning Agent", "Workflow Reviewer",
    )
    descriptors = [
        CapabilityDescriptor(
            capability_id=f"{_capability_slug(role)}.default",
            capability_version=CAPABILITY_VERSION,
            role=role,
            workflow_mode="default",
            telemetry_contract_version=SCHEMA_VERSION,
            quality_eval_profile=f"{QUALITY_EVAL_VERSION}.{_capability_slug(role)}.default",
            change_marker=CAPABILITY_VERSION,
        )
        for role in roles
    ]
    for mode in PM_CAPABILITY_MODES:
        descriptors.append(CapabilityDescriptor(
            capability_id=f"pm.{mode}",
            capability_version=CAPABILITY_VERSION,
            role="PM",
            workflow_mode=mode,
            telemetry_contract_version=SCHEMA_VERSION,
            quality_eval_profile=f"{QUALITY_EVAL_VERSION}.pm.{mode}",
            change_marker=CAPABILITY_VERSION,
        ))
    return descriptors


DEFAULT_CAPABILITY_REGISTRY = CapabilityRegistry(descriptors=_default_capability_descriptors())


def resolve_runtime_capability(role: str, workflow_mode: str) -> CapabilityDescriptor:
    return DEFAULT_CAPABILITY_REGISTRY.resolve(role, workflow_mode)


def validate_capability_coverage(routes: Iterable[tuple[str, str]]) -> list[str]:
    missing: list[str] = []
    for role, mode in sorted(set(routes)):
        try:
            DEFAULT_CAPABILITY_REGISTRY.resolve(role, mode)
        except ValueError:
            missing.append(f"{role}/{mode}")
    return missing


class EfficiencyRunRecord(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    run_id: str = Field(min_length=1)
    trace_id: str = ""
    timestamp: str
    project: str = Field(min_length=1)
    role: str = Field(min_length=1)
    workflow_mode: str = Field(min_length=1)
    capability_id: str = ""
    capability_version: str = ""
    change_marker: str = ""
    quality_eval_profile: str = ""
    execution_backend: str
    contract_version: str = SCHEMA_VERSION
    model: str = "unavailable"
    reasoning_effort: str = "unavailable"
    input_tokens: int | None = Field(default=None, ge=0)
    cached_input_tokens: int | None = Field(default=None, ge=0)
    cache_write_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    reasoning_tokens: int | None = Field(default=None, ge=0)
    model_requests: int | None = Field(default=None, ge=0)
    tool_calls: int | None = Field(default=None, ge=0)
    tool_result_size: int | None = Field(default=None, ge=0)
    context: ContextBreakdown = Field(default_factory=ContextBreakdown)
    latency_seconds: float | None = Field(default=None, ge=0)
    retries: int | None = Field(default=None, ge=0)
    outcome: Literal["success", "failed", "paused", "incomplete"] = "incomplete"
    quality_score: float | None = None
    eval_passed: bool | None = None
    guardrail_passed: bool | None = None
    quality_evidence: WorkflowQualityEvidence | None = None
    estimated_cost_usd: float | None = Field(default=None, ge=0)
    pricing_provenance: str = "unavailable"
    state: Literal["incomplete", "final"] = "final"
    unavailable_fields: list[str] = Field(default_factory=list)
    observation_kind: Literal["operational", "controlled_validation"] = "operational"
    evidence_source: str = "provider_trace"
    source_event_ids: list[str] = Field(default_factory=list)
    evidence_provenance: str = ""
    metric_evidence: dict[str, MetricEvidence] = Field(default_factory=dict)
    latency_breakdown: LatencyBreakdown = Field(default_factory=LatencyBreakdown)

    @model_validator(mode="after")
    def validate_quality_control(self) -> "EfficiencyRunRecord":
        if self.estimated_cost_usd is not None and self.pricing_provenance in {"", "unavailable"}:
            raise ValueError("Estimated cost requires versioned pricing provenance")
        if not self.capability_id:
            self.capability_id = f"legacy.{_capability_slug(self.role)}.{_capability_slug(self.workflow_mode)}"
            self.capability_version = self.capability_version or "legacy-r107"
            self.change_marker = self.change_marker or "legacy-r107"
            self.quality_eval_profile = self.quality_eval_profile or "legacy-unavailable"
        if not all((self.capability_version, self.change_marker, self.quality_eval_profile)):
            raise ValueError("Capability identity requires version, change marker, and eval profile")
        self.source_event_ids = sorted(set(item.strip() for item in self.source_event_ids if item.strip()))
        if self.observation_kind == "controlled_validation" and not self.evidence_source.startswith("controlled:"):
            raise ValueError("Controlled observations require an explicit controlled evidence source")
        if self.evidence_source == "canonical_codex_lifecycle" and self.metric_evidence:
            if set(self.metric_evidence) != set(CODEX_TELEMETRY_METRICS):
                raise ValueError("Canonical Codex observations require complete per-metric evidence")
        if self.evidence_source == "canonical_codex_lifecycle":
            if self.quality_evidence is None:
                if self.quality_score is not None:
                    raise ValueError("Canonical Codex numeric quality requires exact attributable artifact evidence")
                # R110 used successful lifecycle validation as an eval/guardrail proxy. R111
                # reads that legacy shape as unavailable until the exact artifact is attached.
                self.eval_passed = None
                self.guardrail_passed = None
                self.unavailable_fields.extend(["quality_score", "eval_passed", "guardrail_passed"])
            elif self.quality_evidence.status == "attributable":
                if (
                    self.quality_score,
                    self.eval_passed,
                    self.guardrail_passed,
                ) != (
                    self.quality_evidence.quality_score,
                    self.quality_evidence.eval_passed,
                    self.quality_evidence.guardrail_passed,
                ):
                    raise ValueError("Canonical Codex quality fields must match attached artifact evidence")
            elif any(value is not None for value in (self.quality_score, self.eval_passed, self.guardrail_passed)):
                raise ValueError("Unavailable canonical quality evidence cannot carry score or pass results")
        self.unavailable_fields = sorted(set(self.unavailable_fields))
        return self

    @property
    def total_tokens(self) -> int | None:
        values = (self.input_tokens, self.output_tokens, self.reasoning_tokens)
        if all(value is None for value in values):
            return None
        return sum(value or 0 for value in values)

    @property
    def quality_controlled_success(self) -> bool:
        return self.outcome == "success" and self.eval_passed is True and self.guardrail_passed is True


class MetricDistribution(LearningModel):
    sample_count: int = Field(ge=0)
    median: float | None = None
    p75: float | None = None
    p90: float | None = None


class WorkflowBaseline(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    baseline_id: str
    project: str
    role: str
    workflow_mode: str
    capability_id: str = ""
    capability_version: str = ""
    change_marker: str = ""
    quality_eval_profile: str = ""
    quality_compatibility_version: str = ""
    metric_semantics_version: str = BASELINE_METRIC_SEMANTICS_VERSION
    contract_version: str
    window_start: str
    window_end: str
    observed_runs: int
    successful_runs: int
    quality_controlled_successes: int
    confidence: Literal["insufficient", "low", "medium", "high"]
    metrics: dict[str, MetricDistribution]
    retry_rate: float | None = None
    cache_utilisation: float | None = None
    quality_score: float | None = None
    guardrail_pass_rate: float | None = None
    cost_per_successful_quality_controlled_workflow: float | None = None
    pricing_provenance: list[str] = Field(default_factory=list)
    missing_metrics: list[str] = Field(default_factory=list)


class CodexObservationImportReport(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    project: str
    evidence_source: str = "canonical_product_history"
    imported_run_ids: list[str] = Field(default_factory=list)
    existing_run_ids: list[str] = Field(default_factory=list)
    rejected_candidates: dict[str, int] = Field(default_factory=dict)
    capability_counts: dict[str, int] = Field(default_factory=dict)
    baseline_ids: dict[str, str] = Field(default_factory=dict)
    below_threshold: dict[str, str] = Field(default_factory=dict)
    telemetry_report_ids: dict[str, str] = Field(default_factory=dict)
    metric_coverage: dict[str, dict[str, int]] = Field(default_factory=dict)
    comparison_status: dict[str, str] = Field(default_factory=dict)
    quality_report_ids: dict[str, str] = Field(default_factory=dict)
    quality_coverage: dict[str, dict[str, int]] = Field(default_factory=dict)


class OperationalLearningProof(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    project: str
    namespace: str
    controlled: bool = True
    baseline_run_ids: list[str]
    regression_run_ids: list[str]
    candidate_run_ids: list[str]
    monitoring_run_ids: list[str]
    signal_id: str
    queued_request_ids: list[str] = Field(default_factory=list)
    diagnosis_id: str
    experiment_id: str
    experiment_status: Literal["adopted", "rejected", "inconclusive"]
    learning_id: str
    related_learning_ids: list[str]
    post_monitoring_signal_ids: list[str]
    incompatible_state: Literal["rebaselining"]
    limitations: list[str] = Field(default_factory=list)


class WindowComparison(LearningModel):
    role: str
    workflow_mode: str
    baseline_run_ids: list[str]
    comparison_run_ids: list[str]
    baseline: WorkflowBaseline
    comparison: WorkflowBaseline
    changes: dict[str, float | None]


class SignalPolicy(LearningModel):
    relative_change_threshold: float = Field(default=0.20, gt=0)
    quality_change_threshold: float = Field(default=0.03, gt=0)
    fast_minimum_samples: int = Field(default=FAST_MINIMUM_SAMPLES, ge=2)
    slow_minimum_samples: int = Field(default=SLOW_MINIMUM_SAMPLES, ge=5)


class EfficiencySignal(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    signal_id: str
    project: str
    role: str
    workflow_mode: str
    capability_id: str = ""
    baseline_capability_version: str = ""
    comparison_capability_version: str = ""
    cadence: Literal["fast", "slow"]
    metric: str
    baseline_window: str
    comparison_window: str
    observed_change: str
    magnitude: float
    confidence: Literal["low", "medium", "high"]
    suspected_context_categories: list[str] = Field(default_factory=list)
    potential_impact: str
    impact: float = Field(ge=0)
    frequency: float = Field(ge=0)
    estimated_effort: float = Field(gt=0)
    risk: float = Field(gt=0)
    priority: float = Field(ge=0)
    status: Literal["open", "diagnosing", "experimenting", "resolved", "dismissed"] = "open"
    created_at: str


class CapabilityWindowPlan(LearningModel):
    capability_id: str
    cadence: Literal["fast", "slow"]
    state: Literal["unobserved", "warming_up", "baselined", "monitoring", "changed", "rebaselining"]
    comparable_run_count: int = Field(ge=0)
    baseline_run_ids: list[str] = Field(default_factory=list)
    comparison_run_ids: list[str] = Field(default_factory=list)
    compatibility_key: str = ""
    current_capability_version: str = ""
    current_change_marker: str = ""
    reason: str


class CapabilityCoverage(LearningModel):
    capability_id: str
    status: Literal["ready", "missing_quality_evidence", "incompatible_eval_profile", "not_applicable", "unregistered"]
    quality_eval_profile: str = ""
    detail: str


class DetectionOutcome(LearningModel):
    capability_id: str
    lifecycle: dict[str, CapabilityWindowPlan]
    coverage: CapabilityCoverage
    signal_ids: list[str] = Field(default_factory=list)
    queued_request_ids: list[str] = Field(default_factory=list)


class CausalHypothesis(LearningModel):
    explanation: str = Field(min_length=1)
    supporting_evidence: list[str] = Field(min_length=1)
    counter_evidence: list[str] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"]


class ProposedExperiment(LearningModel):
    intervention: str = Field(min_length=1)
    baseline: str = Field(min_length=1)
    candidate: str = Field(min_length=1)
    expected_effect: str = Field(min_length=1)
    success_threshold: str = Field(min_length=1)
    quality_guardrails: list[str] = Field(min_length=1)
    safety_guardrails: list[str] = Field(min_length=1)
    minimum_evidence: str = Field(min_length=1)
    falsification_condition: str = Field(min_length=1)


class OSLearningDiagnosis(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    diagnosis_id: str
    signal_id: str
    observation: str = Field(min_length=1)
    severity: Literal["low", "medium", "high", "critical"]
    hypotheses: list[CausalHypothesis] = Field(min_length=1)
    primary_hypothesis: str = Field(min_length=1)
    proposed_experiment: ProposedExperiment
    change_risk: Literal["low", "medium", "structural"]
    recommended_next_role: Literal["PM", "Architect", "Engineer", "QA", "Product Director"]
    related_prior_learning: list[str] = Field(default_factory=list)
    observations_are_separate_from_inferences: bool

    @model_validator(mode="after")
    def validate_contract(self) -> "OSLearningDiagnosis":
        if not self.observations_are_separate_from_inferences:
            raise ValueError("Diagnosis must distinguish observations from inferences")
        if self.primary_hypothesis not in {item.explanation for item in self.hypotheses}:
            raise ValueError("Primary hypothesis must reference a ranked hypothesis")
        return self


class OptimisationExperiment(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    experiment_id: str
    signal_id: str
    diagnosis_id: str
    hypothesis: str
    intervention: str
    baseline_run_ids: list[str] = Field(min_length=1)
    candidate_run_ids: list[str] = Field(min_length=1)
    expected_effect: str
    success_threshold: float = Field(gt=0)
    maximum_quality_regression: float = Field(default=0.0, ge=0)
    maximum_latency_regression: float = Field(default=0.10, ge=0)
    maximum_retry_rate_increase: float = Field(default=0.0, ge=0)
    safety_guardrails: list[str] = Field(min_length=1)
    minimum_evidence: int = Field(default=5, ge=2)
    falsification_condition: str
    change_risk: Literal["low", "medium", "structural"]
    status: Literal["planned", "running", "adopted", "rejected", "inconclusive", "rolled_back"] = "planned"
    decision_reasons: list[str] = Field(default_factory=list)
    created_at: str
    monitoring_baseline_id: str = ""


class SystemLearning(LearningModel):
    schema_version: Literal[SCHEMA_VERSION] = SCHEMA_VERSION
    learning_id: str
    originating_signal: str
    question: str
    hypothesis: str
    intervention: str
    experiment_id: str
    experiment_evidence: dict[str, Any]
    result: Literal["accepted", "rejected", "inconclusive", "rolled_back", "superseded"]
    conclusion: str
    confidence: Literal["low", "medium", "high"]
    applies_to: list[str] = Field(min_length=1)
    do_not_generalise_to: list[str] = Field(default_factory=list)
    related_requirements: list[str] = Field(default_factory=list)
    supersedes: list[str] = Field(default_factory=list)
    recorded_at: str


def _stable_id(prefix: str, *parts: object) -> str:
    digest = sha256("\x1f".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:20]
    return f"{prefix}-{digest}"


def _percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def _distribution(values: Iterable[float]) -> MetricDistribution:
    materialized = [float(value) for value in values]
    return MetricDistribution(
        sample_count=len(materialized),
        median=float(median(materialized)) if materialized else None,
        p75=_percentile(materialized, 0.75),
        p90=_percentile(materialized, 0.90),
    )


def _confidence(sample_count: int) -> Literal["insufficient", "low", "medium", "high"]:
    if sample_count < FAST_MINIMUM_SAMPLES:
        return "insufficient"
    if sample_count < 10:
        return "low"
    if sample_count < SLOW_MINIMUM_SAMPLES:
        return "medium"
    return "high"


def build_workflow_baseline(records: Iterable[EfficiencyRunRecord], *, role: str, workflow_mode: str) -> WorkflowBaseline:
    selected = sorted(
        [record for record in records if record.role == role and record.workflow_mode == workflow_mode and record.state == "final"],
        key=lambda item: (item.timestamp, item.run_id),
    )
    if not selected:
        raise ValueError("No final observations exist for this role and workflow mode")
    contract_versions = {record.contract_version for record in selected}
    if len(contract_versions) != 1:
        raise ValueError("Incompatible contract versions cannot be pooled into one baseline")
    capability_ids = {record.capability_id for record in selected}
    capability_versions = {record.capability_version for record in selected}
    change_markers = {record.change_marker for record in selected}
    eval_profiles = {record.quality_eval_profile for record in selected}
    quality_compatibility_versions = {
        record.quality_evidence.compatibility_version
        if record.quality_evidence is not None
        else "legacy-direct" if record.quality_score is not None else "unavailable"
        for record in selected
    }
    if len(capability_ids) != 1:
        raise ValueError("Incompatible capabilities cannot be pooled into one baseline")
    if len(capability_versions) != 1 or len(change_markers) != 1:
        raise ValueError("Capability versions and change markers require separate baseline windows")
    if len(eval_profiles) != 1:
        raise ValueError("Incompatible quality-eval profiles cannot be pooled into one baseline")
    if len(quality_compatibility_versions) != 1:
        raise ValueError("Incompatible quality evidence semantics require separate baseline windows")
    qc = [record for record in selected if record.quality_controlled_success]
    successful = [record for record in selected if record.outcome == "success"]
    token_values = [record.total_tokens for record in qc if record.total_tokens is not None]
    request_values = [
        record.model_requests for record in qc
        if "model_requests" not in record.unavailable_fields and record.model_requests is not None
    ]
    latency_values = [
        (
            record.latency_breakdown.agent_execution_seconds
            if record.evidence_source == "canonical_codex_lifecycle"
            else record.latency_seconds
        )
        for record in qc
        if (
            record.latency_breakdown.agent_execution_seconds
            if record.evidence_source == "canonical_codex_lifecycle"
            else record.latency_seconds
        ) is not None
    ]
    cost_values = [record.estimated_cost_usd for record in qc if record.estimated_cost_usd is not None]
    quality_values = [record.quality_score for record in selected if record.quality_score is not None]
    cached = sum(record.cached_input_tokens or 0 for record in selected)
    total_input = sum(record.input_tokens or 0 for record in selected)
    metrics = {
        "tokens_per_successful_workflow": _distribution(value for value in token_values if value is not None),
        "model_calls_per_successful_workflow": _distribution(request_values),
        "latency_seconds": _distribution(value for value in latency_values if value is not None),
        "cost_per_successful_workflow": _distribution(value for value in cost_values if value is not None),
        "input_tokens": _distribution(record.input_tokens for record in selected if record.input_tokens is not None),
        "reasoning_tokens": _distribution(record.reasoning_tokens for record in selected if record.reasoning_tokens is not None),
        "tool_result_size": _distribution(
            record.tool_result_size for record in selected
            if "tool_result_size" not in record.unavailable_fields and record.tool_result_size is not None
        ),
    }
    missing = sorted(name for name, value in metrics.items() if value.sample_count == 0)
    provenance = sorted({record.pricing_provenance for record in selected if record.estimated_cost_usd is not None})
    if not total_input:
        missing.append("cache_utilisation")
    if not quality_values:
        missing.append("quality_score")
    if not qc or len(cost_values) != len(qc):
        missing.append("cost_per_successful_quality_controlled_workflow")
    if not any(record.guardrail_passed is not None for record in selected):
        missing.append("guardrail_pass_rate")
    if not any("retries" not in record.unavailable_fields for record in selected):
        missing.append("retry_rate")
    missing = sorted(set(missing))
    return WorkflowBaseline(
        baseline_id=_stable_id(
            "baseline", role, workflow_mode, selected[0].contract_version,
            selected[0].quality_eval_profile, next(iter(quality_compatibility_versions)),
            BASELINE_METRIC_SEMANTICS_VERSION,
            selected[0].run_id, selected[-1].run_id,
        ),
        project=selected[0].project,
        role=role,
        workflow_mode=workflow_mode,
        capability_id=selected[0].capability_id,
        capability_version=selected[0].capability_version,
        change_marker=selected[0].change_marker,
        quality_eval_profile=selected[0].quality_eval_profile,
        quality_compatibility_version=next(iter(quality_compatibility_versions)),
        metric_semantics_version=BASELINE_METRIC_SEMANTICS_VERSION,
        contract_version=selected[0].contract_version,
        window_start=selected[0].timestamp,
        window_end=selected[-1].timestamp,
        observed_runs=len(selected),
        successful_runs=len(successful),
        quality_controlled_successes=len(qc),
        confidence=_confidence(len(selected)),
        metrics=metrics,
        retry_rate=(
            sum(1 for record in selected if (record.retries or 0) > 0 and "retries" not in record.unavailable_fields)
            / len([record for record in selected if "retries" not in record.unavailable_fields and record.retries is not None])
        ) if any("retries" not in record.unavailable_fields and record.retries is not None for record in selected) else None,
        cache_utilisation=(cached / total_input) if total_input else None,
        quality_score=(sum(quality_values) / len(quality_values)) if quality_values else None,
        guardrail_pass_rate=(
            sum(record.guardrail_passed is True for record in selected if record.guardrail_passed is not None)
            / len([record for record in selected if record.guardrail_passed is not None])
        ) if any(record.guardrail_passed is not None for record in selected) else None,
        cost_per_successful_quality_controlled_workflow=(sum(cost_values) / len(qc)) if qc and len(cost_values) == len(qc) else None,
        pricing_provenance=provenance,
        missing_metrics=missing,
    )


def _relative_change(baseline: float | None, candidate: float | None) -> float | None:
    if baseline is None or candidate is None or baseline == 0:
        return None
    return (candidate - baseline) / abs(baseline)


def compare_baselines(baseline: WorkflowBaseline, comparison: WorkflowBaseline) -> dict[str, float | None]:
    if (
        baseline.role, baseline.workflow_mode, baseline.capability_id,
        baseline.contract_version, baseline.quality_eval_profile, baseline.quality_compatibility_version,
        baseline.metric_semantics_version,
    ) != (
        comparison.role, comparison.workflow_mode, comparison.capability_id,
        comparison.contract_version, comparison.quality_eval_profile, comparison.quality_compatibility_version,
        comparison.metric_semantics_version,
    ):
        raise ValueError("Only compatible capability, role, mode, telemetry, and eval baselines may be compared")
    changes: dict[str, float | None] = {}
    for name in sorted(set(baseline.metrics) | set(comparison.metrics)):
        left = baseline.metrics.get(name)
        right = comparison.metrics.get(name)
        changes[name] = _relative_change(left.median if left else None, right.median if right else None)
    for name in ("retry_rate", "cache_utilisation", "quality_score", "guardrail_pass_rate", "cost_per_successful_quality_controlled_workflow"):
        changes[name] = _relative_change(getattr(baseline, name), getattr(comparison, name))
    return changes


def detect_efficiency_signals(
    baseline: WorkflowBaseline,
    comparison: WorkflowBaseline,
    *,
    policy: SignalPolicy | None = None,
    cadence: Literal["fast", "slow"] = "fast",
) -> list[EfficiencySignal]:
    policy = policy or SignalPolicy()
    minimum = policy.fast_minimum_samples if cadence == "fast" else policy.slow_minimum_samples
    if baseline.observed_runs < minimum or comparison.observed_runs < minimum:
        return []
    changes = compare_baselines(baseline, comparison)
    inverse = {"cache_utilisation", "quality_score", "guardrail_pass_rate"}
    signals: list[EfficiencySignal] = []
    for metric, change in sorted(changes.items()):
        if change is None:
            continue
        threshold = policy.quality_change_threshold if metric in {"quality_score", "guardrail_pass_rate"} else policy.relative_change_threshold
        harmful = -change if metric in inverse else change
        if harmful < threshold:
            continue
        confidence = "high" if min(baseline.observed_runs, comparison.observed_runs) >= SLOW_MINIMUM_SAMPLES else "medium"
        impact = min(5.0, max(1.0, abs(change) / threshold))
        frequency = min(5.0, comparison.observed_runs / minimum)
        risk = 2.0 if metric in {"quality_score", "guardrail_pass_rate"} else 1.0
        context_categories = []
        if metric in {"input_tokens", "tokens_per_successful_workflow", "tool_result_size"}:
            context_categories = ["static_instructions", "project_context", "session_context", "tool_results"]
        priority = impact * frequency * (1.0 if confidence == "medium" else 1.5) / risk
        signals.append(EfficiencySignal(
            signal_id=_stable_id("signal", baseline.baseline_id, comparison.baseline_id, metric, cadence),
            project=baseline.project,
            role=baseline.role,
            workflow_mode=baseline.workflow_mode,
            capability_id=baseline.capability_id,
            baseline_capability_version=baseline.capability_version,
            comparison_capability_version=comparison.capability_version,
            cadence=cadence,
            metric=metric,
            baseline_window=f"{baseline.window_start}/{baseline.window_end}",
            comparison_window=f"{comparison.window_start}/{comparison.window_end}",
            observed_change=f"{change:+.2%}",
            magnitude=abs(change),
            confidence=confidence,
            suspected_context_categories=context_categories,
            potential_impact=f"Material regression in {metric}",
            impact=impact,
            frequency=frequency,
            estimated_effort=1.0,
            risk=risk,
            priority=priority,
            created_at=comparison.window_end,
        ))
    return sorted(signals, key=lambda item: (-item.priority, item.signal_id))


def evaluate_experiment(
    experiment: OptimisationExperiment,
    baseline: WorkflowBaseline,
    candidate: WorkflowBaseline,
) -> OptimisationExperiment:
    reasons: list[str] = []
    if min(baseline.quality_controlled_successes, candidate.quality_controlled_successes) < experiment.minimum_evidence:
        return experiment.model_copy(update={"status": "inconclusive", "decision_reasons": ["insufficient_quality_controlled_evidence"]})
    changes = compare_baselines(baseline, candidate)
    token_change = changes.get("tokens_per_successful_workflow")
    quality_change = changes.get("quality_score")
    latency_change = changes.get("latency_seconds")
    retry_change = changes.get("retry_rate")
    guardrail_change = changes.get("guardrail_pass_rate")
    if quality_change is None or guardrail_change is None:
        reasons.append("missing_quality_or_guardrail_evidence")
    if quality_change is not None and quality_change < -experiment.maximum_quality_regression:
        reasons.append("quality_regression")
    if guardrail_change is not None and guardrail_change < 0:
        reasons.append("guardrail_regression")
    if latency_change is not None and latency_change > experiment.maximum_latency_regression:
        reasons.append("latency_regression")
    if retry_change is not None and retry_change > experiment.maximum_retry_rate_increase:
        reasons.append("retry_regression")
    if token_change is None or token_change > -experiment.success_threshold:
        reasons.append("efficiency_threshold_not_met")
    status = "rejected" if reasons else "adopted"
    return experiment.model_copy(update={
        "status": status,
        "decision_reasons": reasons or ["efficiency_and_all_quality_safety_guardrails_passed"],
        "monitoring_baseline_id": candidate.baseline_id if status == "adopted" else "",
    })


def _compatibility_key(record: EfficiencyRunRecord) -> str:
    return "|".join((
        record.capability_id,
        record.role,
        record.workflow_mode,
        record.contract_version,
        record.quality_eval_profile,
        record.quality_evidence.compatibility_version
        if record.quality_evidence is not None
        else "legacy-direct" if record.quality_score is not None else "quality-unavailable",
    ))


def select_capability_windows(
    records: Iterable[EfficiencyRunRecord],
    *,
    capability_id: str,
    cadence: Literal["fast", "slow"] = "fast",
    policy: SignalPolicy | None = None,
) -> CapabilityWindowPlan:
    policy = policy or SignalPolicy()
    minimum = policy.fast_minimum_samples if cadence == "fast" else policy.slow_minimum_samples
    selected = sorted(
        [item for item in records if item.capability_id == capability_id and item.state == "final"],
        key=lambda item: (item.timestamp, item.run_id),
    )
    if not selected:
        return CapabilityWindowPlan(
            capability_id=capability_id, cadence=cadence, state="unobserved", comparable_run_count=0,
            reason="No final observations exist for this capability.",
        )
    latest = selected[-1]
    compatibility_key = _compatibility_key(latest)
    compatible = [item for item in selected if _compatibility_key(item) == compatibility_key]
    incompatible_history = len(compatible) != len(selected)
    common = {
        "capability_id": capability_id,
        "cadence": cadence,
        "comparable_run_count": len(compatible),
        "compatibility_key": compatibility_key,
        "current_capability_version": latest.capability_version,
        "current_change_marker": latest.change_marker,
    }
    if incompatible_history:
        if len(compatible) < minimum:
            return CapabilityWindowPlan(
                **common, state="rebaselining",
                reason="The latest telemetry or eval contract is incompatible and needs a new baseline.",
            )
        return CapabilityWindowPlan(
            **common,
            state="baselined" if len(compatible) == minimum else "monitoring",
            reason="A separate baseline exists for the latest incompatible measurement contract.",
        )

    marker_order: list[tuple[str, str]] = []
    marker_groups: dict[tuple[str, str], list[EfficiencyRunRecord]] = {}
    for item in compatible:
        marker = (item.capability_version, item.change_marker)
        if marker not in marker_groups:
            marker_order.append(marker)
            marker_groups[marker] = []
        marker_groups[marker].append(item)
    current = marker_groups[marker_order[-1]]
    if len(marker_order) > 1:
        previous = marker_groups[marker_order[-2]]
        if len(current) < minimum:
            return CapabilityWindowPlan(
                **common, state="changed",
                reason=f"A compatible capability change is collecting {minimum} post-change observations.",
            )
        if len(previous) < minimum:
            return CapabilityWindowPlan(
                **common, state="rebaselining",
                reason="The pre-change capability version has insufficient comparable baseline evidence.",
            )
        if len(current) == minimum:
            baseline, comparison = previous[-minimum:], current[-minimum:]
        elif len(current) >= minimum * 2 and len(current) % minimum == 0:
            baseline, comparison = current[-minimum * 2:-minimum], current[-minimum:]
        else:
            return CapabilityWindowPlan(
                **common, state="monitoring",
                reason="The changed capability is between deterministic comparison checkpoints.",
            )
        return CapabilityWindowPlan(
            **common, state="monitoring",
            baseline_run_ids=[item.run_id for item in baseline],
            comparison_run_ids=[item.run_id for item in comparison],
            reason="Comparable non-overlapping capability windows are ready for deterministic detection.",
        )

    if len(current) < minimum:
        return CapabilityWindowPlan(
            **common, state="warming_up",
            reason=f"The capability needs {minimum - len(current)} more comparable observations.",
        )
    if len(current) == minimum:
        return CapabilityWindowPlan(
            **common, state="baselined",
            reason="The initial capability baseline threshold has been reached.",
        )
    if len(current) < minimum * 2 or len(current) % minimum != 0:
        return CapabilityWindowPlan(
            **common, state="monitoring",
            reason="The capability is between deterministic comparison checkpoints.",
        )
    return CapabilityWindowPlan(
        **common, state="monitoring",
        baseline_run_ids=[item.run_id for item in current[-minimum * 2:-minimum]],
        comparison_run_ids=[item.run_id for item in current[-minimum:]],
        reason="Sequential non-overlapping monitoring windows are ready for deterministic detection.",
    )


def assess_capability_coverage(
    capability_id: str,
    records: Iterable[EfficiencyRunRecord],
) -> CapabilityCoverage:
    selected = sorted(
        [item for item in records if item.capability_id == capability_id],
        key=lambda item: (item.timestamp, item.run_id),
    )
    if not selected:
        return CapabilityCoverage(
            capability_id=capability_id, status="missing_quality_evidence",
            detail="No observations exist for this capability.",
        )
    latest = selected[-1]
    try:
        descriptor = resolve_runtime_capability(latest.role, latest.workflow_mode)
    except ValueError:
        return CapabilityCoverage(
            capability_id=capability_id, status="unregistered",
            quality_eval_profile=latest.quality_eval_profile,
            detail="The observed role and mode have no registered capability descriptor.",
        )
    if descriptor.eligibility == "not_applicable":
        return CapabilityCoverage(
            capability_id=capability_id, status="not_applicable",
            detail=descriptor.not_applicable_rationale,
        )
    current = [item for item in selected if item.capability_version == descriptor.capability_version]
    if any(item.quality_eval_profile != descriptor.quality_eval_profile for item in current):
        return CapabilityCoverage(
            capability_id=capability_id, status="incompatible_eval_profile",
            quality_eval_profile=descriptor.quality_eval_profile,
            detail="Current observations do not match the registered quality-eval profile.",
        )
    complete = [
        item for item in current
        if item.quality_score is not None
        and item.eval_passed is not None
        and item.guardrail_passed is not None
    ]
    if not complete:
        return CapabilityCoverage(
            capability_id=capability_id, status="missing_quality_evidence",
            quality_eval_profile=descriptor.quality_eval_profile,
            detail="Quality score, eval result, and guardrail evidence are not yet complete.",
        )
    return CapabilityCoverage(
        capability_id=capability_id, status="ready",
        quality_eval_profile=descriptor.quality_eval_profile,
        detail="Comparable quality and guardrail evidence is available.",
    )


class SystemLearningStore:
    def __init__(self, project_name: str, *, namespace: str = "operational") -> None:
        self.project_name = project_name
        normalized_namespace = _capability_slug(namespace)
        self.namespace = normalized_namespace
        base = control_data_dir(project_name) / "system_learning"
        self.root = base if normalized_namespace == "operational" else base / "validation" / normalized_namespace
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.root / f"{name}.json"

    def _read(self, name: str) -> list[dict[str, Any]]:
        value = load_json(self._path(name), [])
        return value if isinstance(value, list) else []

    def _upsert(self, name: str, identity: str, payload: dict[str, Any]) -> dict[str, Any]:
        with project_lock(self.project_name):
            values = self._read(name)
            matches = [item for item in values if item.get(identity) == payload[identity]]
            if matches:
                if matches[0] != payload:
                    raise ValueError(f"Immutable {name} identity already exists with different content")
                return matches[0]
            values.append(payload)
            atomic_write_json(self._path(name), values)
        return payload

    def record_run(self, record: EfficiencyRunRecord) -> EfficiencyRunRecord:
        payload = record.model_dump(mode="json")
        materialized = record
        with project_lock(self.project_name):
            values = self._read("runs")
            for index, existing in enumerate(values):
                if existing.get("run_id") != record.run_id:
                    continue
                previous = EfficiencyRunRecord.model_validate(existing)
                if previous.state == "incomplete" and record.state == "final":
                    values[index] = payload
                    atomic_write_json(self._path("runs"), values)
                    materialized = record
                    break
                if existing != payload:
                    raise ValueError("Immutable final run identity already exists with different content")
                materialized = previous
                break
            else:
                values.append(payload)
                atomic_write_json(self._path("runs"), values)
        if materialized.state == "final":
            self._process_capability_safely(
                materialized.capability_id,
                trigger_run_id=materialized.run_id,
                queue_diagnosis=False,
            )
        return materialized

    def runs(
        self,
        *,
        role: str = "",
        workflow_mode: str = "",
        capability_id: str = "",
        run_ids: list[str] | None = None,
    ) -> list[EfficiencyRunRecord]:
        identities = set(run_ids or [])
        values = [EfficiencyRunRecord.model_validate(item) for item in self._read("runs")]
        return [
            item for item in values
            if (not role or item.role == role)
            and (not workflow_mode or item.workflow_mode == workflow_mode)
            and (not capability_id or item.capability_id == capability_id)
            and (not identities or item.run_id in identities)
        ]

    def attach_run_evidence(
        self,
        run_id: str,
        *,
        quality_score: float | None = None,
        eval_passed: bool | None = None,
        guardrail_passed: bool | None = None,
        estimated_cost_usd: float | None = None,
        pricing_provenance: str = "",
    ) -> EfficiencyRunRecord:
        updates = {
            "quality_score": quality_score,
            "eval_passed": eval_passed,
            "guardrail_passed": guardrail_passed,
            "estimated_cost_usd": estimated_cost_usd,
        }
        with project_lock(self.project_name):
            values = self._read("runs")
            for index, existing in enumerate(values):
                if existing.get("run_id") != run_id:
                    continue
                record = EfficiencyRunRecord.model_validate(existing)
                for field, value in updates.items():
                    current = getattr(record, field)
                    if value is not None and current is not None and current != value:
                        raise ValueError(f"Run {field} evidence is immutable once recorded")
                if estimated_cost_usd is not None and not pricing_provenance.strip():
                    raise ValueError("Estimated cost evidence requires versioned pricing provenance")
                materialized = record.model_copy(update={
                    **{field: value if value is not None else getattr(record, field) for field, value in updates.items()},
                    "pricing_provenance": pricing_provenance.strip() if estimated_cost_usd is not None else record.pricing_provenance,
                })
                materialized = EfficiencyRunRecord.model_validate(materialized.model_dump(mode="json"))
                values[index] = materialized.model_dump(mode="json")
                atomic_write_json(self._path("runs"), values)
                break
            else:
                raise ValueError("Unknown efficiency run")
        if materialized.state == "final":
            self._process_capability_safely(
                materialized.capability_id,
                trigger_run_id=materialized.run_id,
                queue_diagnosis=True,
            )
        return materialized

    def attach_telemetry_evidence(
        self,
        run_id: str,
        *,
        metric_evidence: dict[str, MetricEvidence],
        latency_breakdown: LatencyBreakdown,
    ) -> EfficiencyRunRecord:
        """Enrich a final run once with attributable R110 telemetry metadata."""
        with project_lock(self.project_name):
            values = self._read("runs")
            for index, existing in enumerate(values):
                if existing.get("run_id") != run_id:
                    continue
                record = EfficiencyRunRecord.model_validate(existing)
                if record.metric_evidence and record.metric_evidence != metric_evidence:
                    raise ValueError("Run metric provenance is immutable once attached")
                empty_latency = LatencyBreakdown()
                if record.latency_breakdown != empty_latency and record.latency_breakdown != latency_breakdown:
                    raise ValueError("Run latency-phase evidence is immutable once attached")
                unavailable_count_fields = {
                    field: None
                    for field in ("model_requests", "tool_calls", "tool_result_size", "retries")
                    if metric_evidence[field].status == "unavailable"
                }
                for field in unavailable_count_fields:
                    if getattr(record, field) not in {None, 0}:
                        raise ValueError(f"Run {field} conflicts with unavailable telemetry evidence")
                materialized = EfficiencyRunRecord.model_validate(record.model_copy(update={
                    "metric_evidence": metric_evidence,
                    "latency_breakdown": latency_breakdown,
                    **unavailable_count_fields,
                }).model_dump(mode="json"))
                values[index] = materialized.model_dump(mode="json")
                atomic_write_json(self._path("runs"), values)
                return materialized
            raise ValueError("Unknown efficiency run")

    def attach_quality_evidence(
        self,
        run_id: str,
        *,
        quality_evidence: WorkflowQualityEvidence,
    ) -> EfficiencyRunRecord:
        """Idempotently enrich one exact operational run with versioned artifact quality evidence."""
        with project_lock(self.project_name):
            values = self._read("runs")
            for index, existing in enumerate(values):
                if existing.get("run_id") != run_id:
                    continue
                record = EfficiencyRunRecord.model_validate(existing)
                if record.observation_kind != "operational" or record.evidence_source != "canonical_codex_lifecycle":
                    raise ValueError("Operational PM quality evidence may attach only to canonical Codex lifecycle records")
                if quality_evidence.workflow_mode != record.workflow_mode:
                    raise ValueError("Quality evidence workflow mode does not match the run")
                if quality_evidence.profile_id != record.quality_eval_profile:
                    raise ValueError("Quality evidence profile does not match the registered capability")
                if record.quality_evidence is not None:
                    if record.quality_evidence != quality_evidence:
                        raise ValueError("Run quality evidence is immutable once attached")
                    return record
                available = quality_evidence.status == "attributable"
                metric_evidence = dict(record.metric_evidence)
                quality_metrics = {
                    "quality_score": ("score_0_to_1", "Deterministic weighted structural quality score for the exact typed PM artifact."),
                    "eval_passed": ("boolean", "The exact artifact meets the versioned profile threshold and quality guardrails."),
                    "guardrail_passed": ("boolean", "The exact artifact passes deterministic safety and authorization checks."),
                }
                for metric, (unit, semantics) in quality_metrics.items():
                    metric_evidence[metric] = MetricEvidence(
                        status="attributable" if available else "unavailable",
                        source="controller_pm_proposal_record" if available else "",
                        unit=unit if available else "",
                        semantics=semantics if available else "",
                        compatibility_version=quality_evidence.compatibility_version,
                        privacy_classification="operational_metadata" if available else "unavailable",
                        source_event_ids=record.source_event_ids if available else [],
                        unavailable_reason="" if available else quality_evidence.unavailable_reason,
                    )
                unavailable_fields = set(record.unavailable_fields)
                if available:
                    unavailable_fields.difference_update(quality_metrics)
                else:
                    unavailable_fields.update(quality_metrics)
                materialized = EfficiencyRunRecord.model_validate(record.model_copy(update={
                    "quality_score": quality_evidence.quality_score if available else None,
                    "eval_passed": quality_evidence.eval_passed if available else None,
                    "guardrail_passed": quality_evidence.guardrail_passed if available else None,
                    "quality_evidence": quality_evidence,
                    "metric_evidence": metric_evidence,
                    "unavailable_fields": sorted(unavailable_fields),
                }).model_dump(mode="json"))
                values[index] = materialized.model_dump(mode="json")
                atomic_write_json(self._path("runs"), values)
                break
            else:
                raise ValueError("Unknown efficiency run")
        if materialized.state == "final" and available:
            self._process_capability_safely(
                materialized.capability_id,
                trigger_run_id=materialized.run_id,
                queue_diagnosis=False,
            )
        return materialized

    def _record_detection_failure(self, capability_id: str, trigger_run_id: str, exc: Exception) -> None:
        payload = {
            "event_id": _stable_id("detection-failure", capability_id, trigger_run_id),
            "capability_id": capability_id,
            "trigger_run_id": trigger_run_id,
            "detail": str(exc)[:500],
        }
        with project_lock(self.project_name):
            values = self._read("detection_events")
            if not any(item.get("event_id") == payload["event_id"] for item in values):
                values.append(payload)
                atomic_write_json(self._path("detection_events"), values)

    def _process_capability_safely(
        self,
        capability_id: str,
        *,
        trigger_run_id: str,
        queue_diagnosis: bool = False,
    ) -> DetectionOutcome | None:
        try:
            return self.process_capability(capability_id, queue_diagnosis=queue_diagnosis)
        except Exception as exc:
            self._record_detection_failure(capability_id, trigger_run_id, exc)
            return None

    def process_capability(
        self,
        capability_id: str,
        *,
        policy: SignalPolicy | None = None,
        queue_diagnosis: bool = False,
    ) -> DetectionOutcome:
        policy = policy or SignalPolicy()
        records = self.runs(capability_id=capability_id)
        coverage = assess_capability_coverage(capability_id, records)
        quality_eligible_records = [
            item for item in records
            if item.quality_score is not None
            and item.eval_passed is not None
            and item.guardrail_passed is not None
        ]
        plans = {
            cadence: select_capability_windows(
                quality_eligible_records, capability_id=capability_id, cadence=cadence, policy=policy
            )
            for cadence in ("fast", "slow")
        }
        detected: dict[str, EfficiencySignal] = {}
        for cadence, plan in plans.items():
            if not plan.baseline_run_ids or not plan.comparison_run_ids:
                continue
            baseline_records = self.runs(run_ids=plan.baseline_run_ids)
            comparison_records = self.runs(run_ids=plan.comparison_run_ids)
            comparison_evidence = baseline_records + comparison_records
            if not comparison_evidence or not all(
                item.quality_score is not None
                and item.eval_passed is not None
                and item.guardrail_passed is not None
                for item in comparison_evidence
            ):
                continue
            exemplar = comparison_records[-1]
            baseline = self.save_baseline(build_workflow_baseline(
                baseline_records, role=exemplar.role, workflow_mode=exemplar.workflow_mode
            ))
            comparison = self.save_baseline(build_workflow_baseline(
                comparison_records, role=exemplar.role, workflow_mode=exemplar.workflow_mode
            ))
            for signal in detect_efficiency_signals(
                baseline, comparison, policy=policy, cadence=cadence
            ):
                try:
                    previous = self.signal(signal.signal_id)
                except ValueError:
                    previous = None
                if previous is not None:
                    signal = signal.model_copy(update={"status": previous.status})
                detected[signal.signal_id] = self.save_signal(signal)
        queued_ids: list[str] = []
        if queue_diagnosis:
            for signal in sorted(detected.values(), key=lambda item: (-item.priority, item.signal_id)):
                if signal.priority < DIAGNOSIS_PRIORITY_THRESHOLD:
                    continue
                queued_ids.append(self.queue_diagnosis(signal).request_id)
        return DetectionOutcome(
            capability_id=capability_id,
            lifecycle=plans,
            coverage=coverage,
            signal_ids=sorted(detected),
            queued_request_ids=sorted(set(queued_ids)),
        )

    def queue_diagnosis(self, signal: EfficiencySignal):
        from control_plane import WorkflowController

        namespace = self.namespace
        request = WorkflowController().create_codex_work_request(
            self.project_name,
            (
                f"Diagnose system-learning signal {signal.signal_id} for capability "
                f"{signal.capability_id} in evidence namespace {namespace} using only the "
                "OS Learning Agent read-only tools. "
                "Return one structured falsifiable diagnosis and governed next-role recommendation."
            ),
            requested_by="deterministic-system-learning",
            source="event-driven-signal-detector",
            requested_role="os_learning_agent",
            idempotency_key=f"os-learning-diagnosis:{signal.signal_id}",
            request_kind="os_learning_diagnosis",
            payload={
                "signal_id": signal.signal_id,
                "capability_id": signal.capability_id,
                "cadence": signal.cadence,
                "read_only": True,
                "namespace": namespace,
            },
        )
        if signal.status == "open":
            self.save_signal(signal.model_copy(update={"status": "diagnosing"}))
        return request

    def save_baseline(self, baseline: WorkflowBaseline) -> WorkflowBaseline:
        return WorkflowBaseline.model_validate(self._upsert("baselines", "baseline_id", baseline.model_dump(mode="json")))

    def baseline(self, *, role: str, workflow_mode: str) -> WorkflowBaseline:
        matches = [WorkflowBaseline.model_validate(item) for item in self._read("baselines") if item.get("role") == role and item.get("workflow_mode") == workflow_mode]
        if matches:
            return sorted(matches, key=lambda item: item.window_end)[-1]
        records = sorted(
            self.runs(role=role, workflow_mode=workflow_mode),
            key=lambda item: (item.timestamp, item.run_id),
        )
        if not records:
            raise ValueError("No final observations exist for this role and workflow mode")
        latest = records[-1]
        current = [
            item for item in records
            if item.state == "final"
            and item.capability_id == latest.capability_id
            and item.capability_version == latest.capability_version
            and item.change_marker == latest.change_marker
            and item.contract_version == latest.contract_version
            and item.quality_eval_profile == latest.quality_eval_profile
        ]
        return self.save_baseline(build_workflow_baseline(
            current, role=role, workflow_mode=workflow_mode
        ))

    def refresh_signal_backlog(
        self,
        *,
        role: str,
        workflow_mode: str,
        baseline_run_ids: list[str],
        comparison_run_ids: list[str],
        cadence: Literal["fast", "slow"] = "fast",
        policy: SignalPolicy | None = None,
    ) -> list[EfficiencySignal]:
        baseline = self.save_baseline(build_workflow_baseline(
            self.runs(run_ids=baseline_run_ids), role=role, workflow_mode=workflow_mode
        ))
        comparison = self.save_baseline(build_workflow_baseline(
            self.runs(run_ids=comparison_run_ids), role=role, workflow_mode=workflow_mode
        ))
        for signal in detect_efficiency_signals(baseline, comparison, policy=policy, cadence=cadence):
            self.save_signal(signal)
        return self.signals(status="open")

    def save_signal(self, signal: EfficiencySignal) -> EfficiencySignal:
        payload = signal.model_dump(mode="json")
        allowed = {
            "open": {"open", "diagnosing", "dismissed"},
            "diagnosing": {"diagnosing", "experimenting", "dismissed"},
            "experimenting": {"experimenting", "resolved", "dismissed"},
            "resolved": {"resolved"},
            "dismissed": {"dismissed"},
        }
        with project_lock(self.project_name):
            values = self._read("signals")
            for index, existing in enumerate(values):
                if existing.get("signal_id") != signal.signal_id:
                    continue
                previous = EfficiencySignal.model_validate(existing)
                if signal.status not in allowed[previous.status]:
                    raise ValueError("Invalid efficiency signal status transition")
                immutable = {key: value for key, value in existing.items() if key != "status"}
                candidate = {key: value for key, value in payload.items() if key != "status"}
                if immutable != candidate:
                    raise ValueError("Signal evidence is immutable after detection")
                values[index] = payload
                atomic_write_json(self._path("signals"), values)
                return signal
            values.append(payload)
            atomic_write_json(self._path("signals"), values)
        return signal

    def signals(self, *, status: str = "") -> list[EfficiencySignal]:
        values = [EfficiencySignal.model_validate(item) for item in self._read("signals")]
        selected = [item for item in values if not status or item.status == status]
        return sorted(selected, key=lambda item: (-item.priority, item.created_at, item.signal_id))

    def signal(self, signal_id: str) -> EfficiencySignal:
        for item in self._read("signals"):
            if item.get("signal_id") == signal_id:
                return EfficiencySignal.model_validate(item)
        raise ValueError("Unknown efficiency signal")

    def save_diagnosis(self, diagnosis: OSLearningDiagnosis) -> OSLearningDiagnosis:
        self.signal(diagnosis.signal_id)
        return OSLearningDiagnosis.model_validate(self._upsert("diagnoses", "diagnosis_id", diagnosis.model_dump(mode="json")))

    def save_experiment(self, experiment: OptimisationExperiment) -> OptimisationExperiment:
        payload = experiment.model_dump(mode="json")
        allowed = {
            "planned": {"planned", "running", "adopted", "rejected", "inconclusive"},
            "running": {"running", "adopted", "rejected", "inconclusive"},
            "adopted": {"adopted", "rolled_back"},
            "rejected": {"rejected"},
            "inconclusive": {"inconclusive"},
            "rolled_back": {"rolled_back"},
        }
        mutable = {"status", "decision_reasons", "monitoring_baseline_id"}
        with project_lock(self.project_name):
            values = self._read("experiments")
            for index, existing in enumerate(values):
                if existing.get("experiment_id") != experiment.experiment_id:
                    continue
                previous = OptimisationExperiment.model_validate(existing)
                if experiment.status not in allowed[previous.status]:
                    raise ValueError("Invalid optimisation experiment status transition")
                if {key: value for key, value in existing.items() if key not in mutable} != {
                    key: value for key, value in payload.items() if key not in mutable
                }:
                    raise ValueError("Experiment design is immutable after creation")
                values[index] = payload
                atomic_write_json(self._path("experiments"), values)
                return experiment
            values.append(payload)
            atomic_write_json(self._path("experiments"), values)
        return experiment

    def experiment(self, experiment_id: str) -> OptimisationExperiment:
        for item in self._read("experiments"):
            if item.get("experiment_id") == experiment_id:
                return OptimisationExperiment.model_validate(item)
        raise ValueError("Unknown optimisation experiment")

    def save_learning(self, learning: SystemLearning) -> SystemLearning:
        return SystemLearning.model_validate(self._upsert("learnings", "learning_id", learning.model_dump(mode="json")))

    def search_learnings(self, query: str, *, limit: int = 10) -> list[SystemLearning]:
        terms = {term.casefold() for term in query.split() if term.strip()}
        scored: list[tuple[int, SystemLearning]] = []
        for item in self._read("learnings"):
            learning = SystemLearning.model_validate(item)
            searchable = " ".join([
                learning.question, learning.hypothesis, learning.intervention, learning.conclusion,
                *learning.applies_to, *learning.do_not_generalise_to,
            ]).casefold()
            score = sum(term in searchable for term in terms)
            if not terms or score:
                scored.append((score, learning))
        return [item for _, item in sorted(scored, key=lambda pair: (-pair[0], pair[1].recorded_at))[:limit]]


def record_from_trace_events(project_name: str, trace_id: str, *, workflow_mode: str = "") -> EfficiencyRunRecord:
    from agents_runtime.support import load_agent_traces

    events = [item for item in load_agent_traces(project_name) if str(item.get("trace_id", "")) == trace_id]
    if not events:
        raise ValueError("No trace events exist for this trace")
    started = next((item for item in events if item.get("event") == "run_started"), events[0])
    terminal = next((item for item in reversed(events) if item.get("event") in {"run_completed", "run_failed", "run_paused"}), events[-1])
    responses = [item for item in events if item.get("event") == "model_response"]
    tools = [item for item in events if item.get("event") == "tool_completed"]
    prompts = [item for item in events if item.get("event") == "model_call"]
    def total(name: str) -> int:
        return sum(int(item.get(name, 0) or 0) for item in responses)
    role = str(started.get("role") or started.get("agent") or "Unknown")
    resolved_mode = workflow_mode or str(started.get("workflow_mode") or "default")
    capability = resolve_runtime_capability(role, resolved_mode)
    outcome = {"run_completed": "success", "run_failed": "failed", "run_paused": "paused"}.get(str(terminal.get("event")), "incomplete")
    guardrails = terminal.get("guardrails", [])
    guardrail_passed = not bool(guardrails) if outcome == "success" else None
    unavailable = []
    if not responses:
        unavailable.extend(["input_tokens", "cached_input_tokens", "cache_write_tokens", "output_tokens", "reasoning_tokens"])
    record = EfficiencyRunRecord(
        run_id=str(started.get("run_id") or trace_id),
        trace_id=trace_id,
        timestamp=str(started.get("timestamp") or datetime.now(timezone.utc).isoformat()),
        project=project_name,
        role=role,
        workflow_mode=resolved_mode,
        capability_id=capability.capability_id,
        capability_version=capability.capability_version,
        change_marker=capability.change_marker,
        quality_eval_profile=capability.quality_eval_profile,
        execution_backend=str(started.get("runtime") or "unknown"),
        contract_version=capability.telemetry_contract_version,
        model=str(started.get("model") or "unavailable"),
        reasoning_effort=str(started.get("reasoning_effort") or "unavailable"),
        input_tokens=total("input_tokens") if responses else None,
        cached_input_tokens=total("cached_input_tokens") if responses else None,
        cache_write_tokens=total("cache_write_tokens") if responses else None,
        output_tokens=total("output_tokens") if responses else None,
        reasoning_tokens=total("reasoning_tokens") if responses else None,
        model_requests=sum(int(item.get("model_requests", 0) or 0) for item in responses) or len(responses),
        tool_calls=len(tools),
        tool_result_size=sum(int(item.get("output_chars", 0) or 0) for item in tools),
        context=ContextBreakdown(
            static_instructions=max([int(item.get("static_instruction_size", 0) or 0) for item in prompts] or [0]),
            project_context=max([int(item.get("project_context_size", 0) or 0) for item in prompts] or [0]),
            session_context=max([int(item.get("session_context_size", 0) or 0) for item in prompts] or [0]),
            tool_results=sum(int(item.get("output_chars", 0) or 0) for item in tools),
        ),
        latency_seconds=float(terminal["latency_seconds"]) if terminal.get("latency_seconds") is not None else None,
        retries=int(terminal.get("retries", 0) or 0),
        outcome=outcome,
        quality_score=float(terminal["quality_score"]) if terminal.get("quality_score") is not None else None,
        eval_passed=bool(terminal["eval_passed"]) if terminal.get("eval_passed") is not None else None,
        guardrail_passed=guardrail_passed,
        unavailable_fields=unavailable,
        state="incomplete" if outcome in {"paused", "incomplete"} else "final",
    )
    store = SystemLearningStore(project_name)
    recorded = store.record_run(record)
    if recorded.state == "final":
        store._process_capability_safely(
            recorded.capability_id,
            trigger_run_id=recorded.run_id,
            queue_diagnosis=True,
        )
    return recorded


def _parse_history_time(value: object) -> datetime:
    normalized = str(value or "").strip().replace("Z", "+00:00")
    if not normalized:
        raise ValueError("Canonical lifecycle evidence is missing a timestamp")
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)


def _history_latency(start: dict[str, Any], end: dict[str, Any]) -> float:
    seconds = (_parse_history_time(end.get("recorded_at")) - _parse_history_time(start.get("recorded_at"))).total_seconds()
    if seconds < 0:
        raise ValueError("Canonical lifecycle timestamps are out of order")
    return seconds


def _codex_native_unavailable_fields(quality_evidence: WorkflowQualityEvidence | None = None) -> list[str]:
    unavailable = [
        "cache_write_tokens", "cached_input_tokens", "context.project_context",
        "context.session_context", "context.static_instructions", "context.tool_results",
        "estimated_cost_usd", "input_tokens", "model", "model_requests", "output_tokens",
        "reasoning_effort", "reasoning_tokens", "retries", "tool_calls",
        "tool_result_size",
    ]
    if quality_evidence is None or quality_evidence.status != "attributable":
        unavailable.extend(["quality_score", "eval_passed", "guardrail_passed"])
    return sorted(unavailable)


def codex_native_telemetry_capability_report(workflow_mode: str) -> CodexTelemetryCapabilityReport:
    if workflow_mode not in {"requirement_draft", "task_plan"}:
        raise ValueError("Codex-native telemetry audit supports requirement_draft and task_plan")
    unavailable = {
        "model": "The canonical lifecycle does not record the Codex host model.",
        "reasoning_effort": "The canonical lifecycle does not record Codex reasoning configuration.",
        "input_tokens": "The Codex host does not expose attributable input usage in canonical history.",
        "cached_input_tokens": "The Codex host does not expose attributable cache-read usage in canonical history.",
        "cache_write_tokens": "The Codex host does not expose attributable cache-write usage in canonical history.",
        "output_tokens": "The Codex host does not expose attributable output usage in canonical history.",
        "reasoning_tokens": "The Codex host does not expose attributable reasoning usage in canonical history.",
        "model_requests": "Controller events do not prove the number of Codex model requests.",
        "tool_calls": "Controller events do not prove the number of model-visible tool calls.",
        "tool_result_size": "Canonical history omits model-visible tool payload sizes.",
        "context.static_instructions": "Canonical history does not retain instruction payload sizes.",
        "context.project_context": "Canonical history does not retain project-context payload sizes.",
        "context.session_context": "Canonical history does not retain conversation-context payload sizes.",
        "context.tool_results": "Canonical history does not retain tool-result payload sizes.",
        "retries": "Controller retries cannot be treated as provider or model retries.",
        "quality_score": "No numeric quality evaluation is attached to canonical Codex lifecycle events.",
        "eval_passed": "Lifecycle completion is not a quality evaluation; an exact compatible artifact profile is required.",
        "guardrail_passed": "Approval is not a quality guardrail result; exact deterministic artifact evidence is required.",
        "estimated_cost_usd": "Cost requires attributable provider usage, which is unavailable.",
        "pricing_provenance": "Pricing cannot be applied without attributable provider usage and model identity.",
    }
    phase_unavailable = {
        "requirement_draft": {
            "latency.agent_execution": "Model execution ends before proposal submission and has no canonical start boundary.",
            "latency.controller": "No non-overlapping controller interval is isolated inside the approval wait.",
            "latency.queue_wait": "Requirement drafting has no canonical Codex work-queue interval.",
        },
        "task_plan": {
            "latency.governance_wait": "Authorized task plans auto-apply and contain no Product Director wait interval.",
        },
    }[workflow_mode]
    direct = {
        "outcome": (
            "canonical_terminal_event", "state",
            "Successful exact approval or completed linked work-request resolution."
        ),
    }
    derived = {
        "latency.total_lifecycle": (
            "canonical_event_timestamps", "seconds",
            "Elapsed wall time across the complete admitted canonical lifecycle."
        ),
    }
    if workflow_mode == "requirement_draft":
        derived["latency.governance_wait"] = (
            "proposal_submitted_to_approved", "seconds",
            "Elapsed Product Director governance wait after the Codex PM proposal was submitted."
        )
    else:
        derived.update({
            "latency.queue_wait": (
                "work_requested_to_claimed", "seconds",
                "Elapsed time before a Codex host claimed the authorized PM task-plan request."
            ),
            "latency.agent_execution": (
                "work_claimed_to_task_plan_applied", "seconds",
                "Active Codex-agent task-plan interval; provider-only model time remains unavailable."
            ),
            "latency.controller": (
                "task_plan_applied_to_work_resolved", "seconds",
                "Deterministic controller closure interval after exact task-plan application."
            ),
        })
    assessments: list[TelemetrySourceAssessment] = []
    for metric in CODEX_TELEMETRY_METRICS:
        if metric in direct:
            source, unit, semantics = direct[metric]
            assessments.append(TelemetrySourceAssessment(
                metric=metric, status="attributable", source=source, unit=unit,
                semantics=semantics, privacy_classification="operational_metadata",
            ))
        elif metric in derived:
            source, unit, semantics = derived[metric]
            assessments.append(TelemetrySourceAssessment(
                metric=metric, status="derived", source=source, unit=unit,
                semantics=semantics, privacy_classification="operational_metadata",
            ))
        else:
            assessments.append(TelemetrySourceAssessment(
                metric=metric, status="unavailable", privacy_classification="unavailable",
                limitation=phase_unavailable.get(metric, unavailable.get(metric, "No attributable canonical source exists.")),
            ))
    return CodexTelemetryCapabilityReport(
        report_id=_stable_id("codex-telemetry-report", CODEX_TELEMETRY_COMPATIBILITY_VERSION, workflow_mode),
        workflow_mode=workflow_mode,
        assessments=assessments,
    )


def _metric_evidence_from_report(
    workflow_mode: str,
    source_event_ids: list[str],
    quality_evidence: WorkflowQualityEvidence | None = None,
) -> dict[str, MetricEvidence]:
    report = codex_native_telemetry_capability_report(workflow_mode)
    evidence = {
        item.metric: MetricEvidence(
            status=item.status,
            source=item.source,
            unit=item.unit,
            semantics=item.semantics,
            compatibility_version=item.compatibility_version,
            privacy_classification=item.privacy_classification,
            source_event_ids=source_event_ids if item.status != "unavailable" else [],
            unavailable_reason=item.limitation,
        )
        for item in report.assessments
    }
    if quality_evidence is not None and quality_evidence.status == "attributable":
        for metric, unit, semantics in (
            ("quality_score", "score_0_to_1", "Deterministic weighted structural quality score for the exact typed PM artifact."),
            ("eval_passed", "boolean", "The exact artifact meets the versioned profile threshold and quality guardrails."),
            ("guardrail_passed", "boolean", "The exact artifact passes the profile's deterministic safety and authorization checks."),
        ):
            evidence[metric] = MetricEvidence(
                status="attributable",
                source="controller_pm_proposal_record",
                unit=unit,
                semantics=semantics,
                compatibility_version=quality_evidence.compatibility_version,
                privacy_classification="operational_metadata",
                source_event_ids=source_event_ids,
            )
    return evidence


def _requirement_draft_latency(
    submitted: dict[str, Any],
    approved: dict[str, Any],
) -> LatencyBreakdown:
    governance = _history_latency(submitted, approved)
    return LatencyBreakdown(
        governance_wait_seconds=governance,
        total_lifecycle_seconds=governance,
        unavailable_phases={
            "agent_execution_seconds": "No canonical model-execution start boundary exists.",
            "controller_seconds": "No isolated non-overlapping controller interval exists.",
            "queue_wait_seconds": "Requirement drafting has no canonical work-queue interval.",
        },
        boundary_provenance="proposal_submitted -> pm_proposal_approved",
    )


def _task_plan_latency(
    requested: dict[str, Any],
    claimed: dict[str, Any],
    applied: dict[str, Any],
    resolved: dict[str, Any],
) -> LatencyBreakdown:
    return LatencyBreakdown(
        queue_wait_seconds=_history_latency(requested, claimed),
        agent_execution_seconds=_history_latency(claimed, applied),
        controller_seconds=_history_latency(applied, resolved),
        total_lifecycle_seconds=_history_latency(requested, resolved),
        unavailable_phases={
            "governance_wait_seconds": "Authorized task plans auto-apply without a Product Director wait interval.",
        },
        boundary_provenance="work_requested -> claimed -> task_plan_auto_applied -> work_resolved",
    )


def _codex_native_record(
    project_name: str,
    *,
    run_id: str,
    workflow_mode: str,
    started: dict[str, Any],
    completed: dict[str, Any],
    source_event_ids: list[str],
    provenance: str,
    latency_breakdown: LatencyBreakdown,
    quality_evidence: WorkflowQualityEvidence | None = None,
) -> EfficiencyRunRecord:
    capability = resolve_runtime_capability("PM", workflow_mode)
    return EfficiencyRunRecord(
        run_id=run_id,
        timestamp=str(started.get("recorded_at", "")),
        project=project_name,
        role="PM",
        workflow_mode=workflow_mode,
        capability_id=capability.capability_id,
        capability_version=capability.capability_version,
        change_marker=capability.change_marker,
        quality_eval_profile=capability.quality_eval_profile,
        execution_backend="codex_native",
        contract_version=capability.telemetry_contract_version,
        latency_seconds=_history_latency(started, completed),
        outcome="success",
        quality_score=quality_evidence.quality_score if quality_evidence and quality_evidence.status == "attributable" else None,
        eval_passed=quality_evidence.eval_passed if quality_evidence and quality_evidence.status == "attributable" else None,
        guardrail_passed=quality_evidence.guardrail_passed if quality_evidence and quality_evidence.status == "attributable" else None,
        quality_evidence=quality_evidence,
        state="final",
        unavailable_fields=_codex_native_unavailable_fields(quality_evidence),
        observation_kind="operational",
        evidence_source="canonical_codex_lifecycle",
        source_event_ids=source_event_ids,
        evidence_provenance=provenance,
        metric_evidence=_metric_evidence_from_report(workflow_mode, source_event_ids, quality_evidence),
        latency_breakdown=latency_breakdown,
    )


def import_codex_native_history(
    project_name: str,
    *,
    events: Iterable[dict[str, Any]] | None = None,
    artifacts: Iterable[dict[str, Any]] | None = None,
    store: SystemLearningStore | None = None,
) -> CodexObservationImportReport:
    """Import only canonical event sequences that prove a completed Codex-native PM workflow."""
    materialized = list(events) if events is not None else read_history(project_name, limit=10_000)
    target = store or SystemLearningStore(project_name)
    existing = {item.run_id for item in target.runs()}
    artifact_values = list(artifacts) if artifacts is not None else load_json(
        control_data_dir(project_name) / "pm_proposals.json", []
    )
    artifact_index: dict[tuple[str, int], dict[str, Any]] = {}
    ambiguous_artifacts: set[tuple[str, int]] = set()
    for item in artifact_values if isinstance(artifact_values, list) else []:
        if not isinstance(item, dict):
            continue
        identity = (str(item.get("proposal_id", "")), int(item.get("proposal_revision", 0) or 0))
        if not identity[0] or identity[1] <= 0:
            continue
        if identity in artifact_index and artifact_index[identity] != item:
            ambiguous_artifacts.add(identity)
        artifact_index[identity] = item
    imported: list[str] = []
    already_present: list[str] = []
    rejected: dict[str, int] = {}

    def reject(reason: str) -> None:
        rejected[reason] = rejected.get(reason, 0) + 1

    def belongs_to_project(event: dict[str, Any]) -> bool:
        declared = str(event.get("project_name") or event.get("project") or "").strip()
        return not declared or declared == project_name

    def persist(record: EfficiencyRunRecord) -> None:
        if record.run_id in existing:
            previous = target.runs(run_ids=[record.run_id])[0]
            if not previous.metric_evidence:
                target.attach_telemetry_evidence(
                    record.run_id,
                    metric_evidence=record.metric_evidence,
                    latency_breakdown=record.latency_breakdown,
                )
            if record.quality_evidence is not None and previous.quality_evidence is None:
                target.attach_quality_evidence(record.run_id, quality_evidence=record.quality_evidence)
            already_present.append(record.run_id)
            return
        target.record_run(record)
        existing.add(record.run_id)
        imported.append(record.run_id)

    approved = {
        (str(item.get("proposal_id", "")), int(item.get("proposal_revision", 0) or 0)): item
        for item in materialized
        if item.get("event_type") == "pm_proposal_approved"
        and item.get("mode") == "requirement_draft"
        and str(item.get("source", "")).startswith("codex")
    }
    for submitted in materialized:
        if submitted.get("event_type") != "pm_proposal_submitted" or submitted.get("mode") != "requirement_draft":
            continue
        if not belongs_to_project(submitted):
            reject("cross_project_requirement_draft")
            continue
        if not str(submitted.get("source", "")).startswith("codex") or str(submitted.get("origin_sdk_run_id", "")):
            reject("non_codex_native_requirement_draft")
            continue
        identity = (str(submitted.get("proposal_id", "")), int(submitted.get("proposal_revision", 0) or 0))
        completed = approved.get(identity)
        if completed is None:
            reject("requirement_draft_without_exact_approval")
            continue
        run_id = _stable_id("codex-run", project_name, "requirement_draft", *identity)
        try:
            source_ids = [str(submitted.get("event_id", "")), str(completed.get("event_id", ""))]
            quality = evaluate_pm_quality_artifact(
                project_name,
                None if identity in ambiguous_artifacts else artifact_index.get(identity),
                workflow_mode="requirement_draft",
                proposal_id=identity[0],
                proposal_revision=identity[1],
            )
            record = _codex_native_record(
                project_name,
                run_id=run_id,
                workflow_mode="requirement_draft",
                started=submitted,
                completed=completed,
                source_event_ids=source_ids,
                provenance="Exact Codex PM proposal submission and Product Director approval recorded in canonical history.",
                latency_breakdown=_requirement_draft_latency(submitted, completed),
                quality_evidence=quality,
            )
            persist(record)
        except (TypeError, ValueError):
            reject("invalid_requirement_draft_telemetry")

    requested = {
        str(item.get("request_id", "")): item
        for item in materialized
        if item.get("event_type") == "codex_work_requested"
    }
    claimed = {
        str(item.get("request_id", "")): item
        for item in materialized
        if item.get("event_type") == "codex_work_claimed"
    }
    resolved = {
        str(item.get("request_id", "")): item
        for item in materialized
        if item.get("event_type") == "codex_work_resolved"
    }
    for applied in materialized:
        if applied.get("event_type") != "pm_derived_task_plan_auto_applied":
            continue
        if not belongs_to_project(applied):
            reject("cross_project_task_plan")
            continue
        request_id = str(applied.get("origin_request_id", ""))
        start = claimed.get(request_id)
        request = requested.get(request_id)
        completion = resolved.get(request_id)
        if (
            not request_id or request is None or start is None or completion is None
            or str(request.get("requested_role", "")).casefold() != "pm"
            or str(request.get("request_kind", "")) != "pm_decision"
            or str(start.get("actor", "")).casefold() != "codex"
            or not str(applied.get("source", "")).startswith("codex")
            or str(applied.get("origin_sdk_run_id", ""))
            or str(completion.get("status", "")) != "COMPLETED"
            or str(completion.get("result_proposal_id", "")) != str(applied.get("proposal_id", ""))
            or int(completion.get("result_proposal_revision", 0) or 0) != int(applied.get("proposal_revision", 0) or 0)
        ):
            reject("incomplete_or_ambiguous_task_plan_sequence")
            continue
        run_id = _stable_id("codex-run", project_name, "task_plan", request_id, applied.get("proposal_id", ""), applied.get("proposal_revision", 0))
        try:
            source_ids = [
                str(request.get("event_id", "")), str(start.get("event_id", "")),
                str(applied.get("event_id", "")), str(completion.get("event_id", "")),
            ]
            task_identity = (
                str(applied.get("proposal_id", "")),
                int(applied.get("proposal_revision", 0) or 0),
            )
            quality = evaluate_pm_quality_artifact(
                project_name,
                None if task_identity in ambiguous_artifacts else artifact_index.get(task_identity),
                workflow_mode="task_plan",
                proposal_id=task_identity[0],
                proposal_revision=task_identity[1],
            )
            record = _codex_native_record(
                project_name,
                run_id=run_id,
                workflow_mode="task_plan",
                started=start,
                completed=applied,
                source_event_ids=source_ids,
                provenance="Claimed Codex PM task-plan request, exact auto-applied proposal, and completed controller resolution recorded in canonical history.",
                latency_breakdown=_task_plan_latency(request, start, applied, completion),
                quality_evidence=quality,
            )
            persist(record)
        except (TypeError, ValueError):
            reject("invalid_task_plan_telemetry")

    capability_counts: dict[str, int] = {}
    baseline_ids: dict[str, str] = {}
    below_threshold: dict[str, str] = {}
    telemetry_report_ids: dict[str, str] = {}
    metric_coverage: dict[str, dict[str, int]] = {}
    comparison_status: dict[str, str] = {}
    quality_report_ids: dict[str, str] = {}
    quality_coverage: dict[str, dict[str, int]] = {}
    for mode in ("requirement_draft", "task_plan"):
        capability = resolve_runtime_capability("PM", mode)
        audit = codex_native_telemetry_capability_report(mode)
        quality_audit = codex_native_quality_capability_report(mode)
        telemetry_report_ids[mode] = audit.report_id
        quality_report_ids[mode] = quality_audit.report_id
        metric_coverage[mode] = {
            status: sum(item.status == status for item in audit.assessments)
            for status in ("attributable", "derived", "unavailable")
        }
        records = target.runs(capability_id=capability.capability_id)
        capability_counts[capability.capability_id] = len(records)
        quality_coverage[mode] = {
            status: sum(
                item.quality_evidence is not None and item.quality_evidence.status == status
                for item in records
            )
            for status in ("attributable", "unavailable", "incompatible")
        }
        eligible = [
            item for item in records
            if item.state == "final"
            and item.quality_score is not None
            and item.eval_passed is not None
            and item.guardrail_passed is not None
        ]
        minimum_for_comparison = FAST_MINIMUM_SAMPLES * 2 if mode == "task_plan" else FAST_MINIMUM_SAMPLES
        if len(eligible) < minimum_for_comparison:
            below_threshold[capability.capability_id] = (
                f"{minimum_for_comparison - len(eligible)} more compatible quality-controlled observations required."
            )
            continue
        baseline_ids[capability.capability_id] = target.save_baseline(
            build_workflow_baseline(eligible, role="PM", workflow_mode=mode)
        ).baseline_id
        outcome = target.process_capability(capability.capability_id, queue_diagnosis=False)
        checkpoint_detail = ""
        checkpoint_signal_ids = list(outcome.signal_ids)
        if mode == "task_plan" and len(eligible) >= FAST_MINIMUM_SAMPLES * 2:
            checkpoint_count = (len(eligible) // FAST_MINIMUM_SAMPLES) * FAST_MINIMUM_SAMPLES
            checkpoint = eligible[checkpoint_count - FAST_MINIMUM_SAMPLES * 2:checkpoint_count]
            checkpoint_baseline = target.save_baseline(build_workflow_baseline(
                checkpoint[:FAST_MINIMUM_SAMPLES], role="PM", workflow_mode=mode,
            ))
            checkpoint_comparison = target.save_baseline(build_workflow_baseline(
                checkpoint[FAST_MINIMUM_SAMPLES:], role="PM", workflow_mode=mode,
            ))
            checkpoint_signal_ids = [
                target.save_signal(item).signal_id
                for item in detect_efficiency_signals(
                    checkpoint_baseline, checkpoint_comparison, cadence="fast"
                )
            ]
            checkpoint_detail = (
                f" Latest completed checkpoint used {FAST_MINIMUM_SAMPLES}+{FAST_MINIMUM_SAMPLES} "
                f"non-overlapping runs through qualified observation {checkpoint_count}; "
                f"{len(eligible) - checkpoint_count} later qualified observation(s) remain between checkpoints."
            )
        comparison_status[capability.capability_id] = (
            f"{outcome.lifecycle['fast'].state}: {outcome.lifecycle['fast'].reason} "
            f"Quality coverage is {outcome.coverage.status}: {outcome.coverage.detail} "
            f"Detected signals: {len(checkpoint_signal_ids)}.{checkpoint_detail}"
        )
    return CodexObservationImportReport(
        project=project_name,
        imported_run_ids=sorted(set(imported)),
        existing_run_ids=sorted(set(already_present)),
        rejected_candidates=dict(sorted(rejected.items())),
        capability_counts=capability_counts,
        baseline_ids=baseline_ids,
        below_threshold=below_threshold,
        telemetry_report_ids=telemetry_report_ids,
        metric_coverage=metric_coverage,
        comparison_status=comparison_status,
        quality_report_ids=quality_report_ids,
        quality_coverage=quality_coverage,
    )


def run_isolated_operational_proof(
    project_name: str,
    *,
    namespace: str = "r109-controlled-v1",
    queue_diagnosis: bool = False,
) -> OperationalLearningProof:
    """Exercise the complete loop with visibly controlled data in a separate store namespace."""
    store = SystemLearningStore(project_name, namespace=namespace)
    existing_proofs = store._read("proofs")
    if existing_proofs:
        return OperationalLearningProof.model_validate(existing_proofs[0])
    capability = resolve_runtime_capability("PM", "task_plan")
    origin = datetime(2026, 8, 23, tzinfo=timezone.utc)

    def controlled_run(index: int, *, tokens: int, quality: float, marker: str, version: str, contract: str = SCHEMA_VERSION) -> EfficiencyRunRecord:
        return EfficiencyRunRecord(
            run_id=_stable_id("controlled-run", project_name, namespace, index, marker),
            timestamp=(origin.replace(minute=0) + timedelta(minutes=index)).isoformat(),
            project=project_name,
            role="PM",
            workflow_mode="task_plan",
            capability_id=capability.capability_id,
            capability_version=version,
            change_marker=marker,
            quality_eval_profile=capability.quality_eval_profile if contract == SCHEMA_VERSION else f"{capability.quality_eval_profile}.incompatible",
            execution_backend="controlled_validation",
            contract_version=contract,
            model="controlled-fixture",
            reasoning_effort="controlled",
            input_tokens=tokens - 20,
            cached_input_tokens=20,
            cache_write_tokens=0,
            output_tokens=20,
            reasoning_tokens=0,
            model_requests=1,
            tool_calls=1,
            tool_result_size=40,
            context=ContextBreakdown(static_instructions=20, project_context=20, session_context=20, tool_results=40),
            latency_seconds=1.2 if tokens >= 120 else 0.9,
            retries=0,
            outcome="success",
            quality_score=quality,
            eval_passed=True,
            guardrail_passed=True,
            estimated_cost_usd=0.01,
            pricing_provenance="controlled-pricing-v1",
            observation_kind="controlled_validation",
            evidence_source=f"controlled:{namespace}",
            evidence_provenance="Sealed R109 controlled comparison evidence; never an operational observation.",
        )

    baseline = [controlled_run(index, tokens=100, quality=0.95, marker="baseline-v1", version="controlled-v1") for index in range(5)]
    regression = [controlled_run(5 + index, tokens=150, quality=0.95, marker="baseline-v1", version="controlled-v1") for index in range(5)]
    candidate = [controlled_run(10 + index, tokens=80, quality=0.96, marker="candidate-v1", version="controlled-v2") for index in range(5)]
    monitoring = [controlled_run(15 + index, tokens=120, quality=0.90, marker="candidate-v1", version="controlled-v2") for index in range(5)]
    for record in baseline + regression:
        store.record_run(record)
    original_signals = store.signals()
    token_signal = next(item for item in original_signals if item.metric == "tokens_per_successful_workflow")
    queued_ids: list[str] = []
    if queue_diagnosis:
        queued_ids = sorted({store.queue_diagnosis(token_signal).request_id, store.queue_diagnosis(token_signal).request_id})
        token_signal = store.signal(token_signal.signal_id)
    elif token_signal.status == "open":
        token_signal = store.save_signal(token_signal.model_copy(update={"status": "diagnosing"}))

    prior = store.search_learnings("controlled scoped task planning")
    hypothesis = CausalHypothesis(
        explanation="The controlled context expansion caused the measured token and latency regression.",
        supporting_evidence=[token_signal.observed_change, token_signal.baseline_window, token_signal.comparison_window],
        counter_evidence=["The controlled quality and guardrail results remained stable."],
        confidence="medium",
    )
    diagnosis = OSLearningDiagnosis(
        diagnosis_id=_stable_id("diagnosis", token_signal.signal_id, namespace),
        signal_id=token_signal.signal_id,
        observation=f"Controlled validation measured {token_signal.observed_change} for {token_signal.metric}.",
        severity="medium",
        hypotheses=[hypothesis],
        primary_hypothesis=hypothesis.explanation,
        proposed_experiment=ProposedExperiment(
            intervention="Use the smaller controlled context composition.",
            baseline="The controlled regressed window.",
            candidate="The controlled scoped-context window.",
            expected_effect="At least 20% fewer tokens with no quality, safety, retry, or latency regression.",
            success_threshold="At least 20% lower tokens per quality-controlled success.",
            quality_guardrails=["No quality-score regression.", "All evals pass."],
            safety_guardrails=["All guardrails pass.", "No approval or authority change."],
            minimum_evidence="Five comparable quality-controlled observations per arm.",
            falsification_condition="Efficiency misses 20% or any quality, guardrail, retry, latency, or comparability check fails.",
        ),
        change_risk="medium",
        recommended_next_role="Architect",
        related_prior_learning=[item.learning_id for item in prior],
        observations_are_separate_from_inferences=True,
    )
    store.save_diagnosis(diagnosis)
    current_signal = store.signal(token_signal.signal_id)
    if current_signal.status == "diagnosing":
        store.save_signal(current_signal.model_copy(update={"status": "experimenting"}))
    for record in candidate:
        store.record_run(record)
    experiment = OptimisationExperiment(
        experiment_id=_stable_id("experiment", diagnosis.diagnosis_id, namespace),
        signal_id=token_signal.signal_id,
        diagnosis_id=diagnosis.diagnosis_id,
        hypothesis=hypothesis.explanation,
        intervention="Use the smaller controlled context composition.",
        baseline_run_ids=[item.run_id for item in regression],
        candidate_run_ids=[item.run_id for item in candidate],
        expected_effect="At least 20% fewer tokens with quality and safety preserved.",
        success_threshold=0.20,
        maximum_quality_regression=0.0,
        maximum_latency_regression=0.0,
        maximum_retry_rate_increase=0.0,
        safety_guardrails=["All guardrails pass.", "Approval semantics remain unchanged."],
        minimum_evidence=5,
        falsification_condition="Any efficiency, quality, safety, retry, latency, or comparability threshold fails.",
        change_risk="medium",
        created_at=(origin.replace(minute=0) + timedelta(minutes=15)).isoformat(),
    )
    store.save_experiment(experiment)
    evaluated = evaluate_experiment(
        experiment,
        build_workflow_baseline(regression, role="PM", workflow_mode="task_plan"),
        build_workflow_baseline(candidate, role="PM", workflow_mode="task_plan"),
    )
    store.save_experiment(evaluated)
    learning = SystemLearning(
        learning_id=_stable_id("learning", evaluated.experiment_id, evaluated.status),
        originating_signal=token_signal.signal_id,
        question="Does controlled scoped context reverse the task-planning efficiency regression without weakening quality or safety?",
        hypothesis=hypothesis.explanation,
        intervention=experiment.intervention,
        experiment_id=experiment.experiment_id,
        experiment_evidence={"decision_reasons": evaluated.decision_reasons, "controlled": True},
        result="accepted" if evaluated.status == "adopted" else "rejected" if evaluated.status == "rejected" else "inconclusive",
        conclusion="The controlled candidate passed the defined efficiency, quality, safety, retry, latency, and evidence thresholds." if evaluated.status == "adopted" else "The controlled candidate did not satisfy every adoption threshold.",
        confidence="medium",
        applies_to=["controlled:PM/task_plan"],
        do_not_generalise_to=["operational workflows", "PM/discovery"],
        related_requirements=["R109"],
        recorded_at=(origin.replace(minute=0) + timedelta(minutes=16)).isoformat(),
    )
    store.save_learning(learning)
    active_signal = store.signal(token_signal.signal_id)
    if active_signal.status == "experimenting":
        store.save_signal(active_signal.model_copy(update={"status": "resolved"}))

    for record in monitoring:
        store.record_run(record)
    post = store.process_capability(capability.capability_id, queue_diagnosis=False)
    incompatible = controlled_run(
        20, tokens=90, quality=0.96, marker="incompatible-v2", version="controlled-v3",
        contract=f"{SCHEMA_VERSION}.incompatible",
    )
    store.record_run(incompatible)
    incompatible_plan = select_capability_windows(
        store.runs(capability_id=capability.capability_id), capability_id=capability.capability_id
    )
    related = store.search_learnings("controlled scoped task planning")
    proof = OperationalLearningProof(
        project=project_name,
        namespace=store.namespace,
        baseline_run_ids=[item.run_id for item in baseline],
        regression_run_ids=[item.run_id for item in regression],
        candidate_run_ids=[item.run_id for item in candidate],
        monitoring_run_ids=[item.run_id for item in monitoring],
        signal_id=token_signal.signal_id,
        queued_request_ids=queued_ids,
        diagnosis_id=diagnosis.diagnosis_id,
        experiment_id=evaluated.experiment_id,
        experiment_status=evaluated.status,
        learning_id=learning.learning_id,
        related_learning_ids=[item.learning_id for item in related],
        post_monitoring_signal_ids=post.signal_ids,
        incompatible_state=incompatible_plan.state,
        limitations=[
            "Controlled evidence is isolated from operational baselines.",
            "No provider or Codex token usage was incurred or inferred.",
            "This fast-loop proof does not establish slow-loop evidence.",
        ],
    )
    store._upsert("proofs", "namespace", proof.model_dump(mode="json"))
    return proof


def inspect_related_repo_changes(project_name: str, *, requirement_id: str = "", limit: int = 20) -> list[dict[str, Any]]:
    events = read_history(project_name, limit=200)
    results = []
    for event in reversed(events):
        if requirement_id and str(event.get("requirement_id", "")) != requirement_id:
            continue
        files = event.get("files_changed")
        if isinstance(files, list) and files:
            results.append({
                "event_id": event.get("event_id", ""),
                "recorded_at": event.get("recorded_at", ""),
                "requirement_id": event.get("requirement_id", ""),
                "files_changed": [str(item) for item in files][:50],
                "summary": str(event.get("summary", ""))[:1_000],
            })
        if len(results) >= limit:
            break
    return results


def inspect_relevant_code(paths: list[str], *, max_chars: int = 20_000) -> dict[str, str]:
    repository = project_path("os-control-panel").parents[1].resolve()
    output: dict[str, str] = {}
    remaining = max_chars
    for raw in paths[:10]:
        normalized = raw.strip().lstrip("/")
        if not any(normalized.startswith(prefix) for prefix in SAFE_CODE_PREFIXES):
            raise ValueError(f"Path is outside the OS Learning Agent code allowlist: {raw}")
        path = (repository / normalized).resolve()
        if repository not in path.parents or not path.is_file():
            raise ValueError(f"Relevant code path does not exist: {raw}")
        text = path.read_text(encoding="utf-8")[:remaining]
        output[normalized] = text
        remaining -= len(text)
        if remaining <= 0:
            break
    return output
