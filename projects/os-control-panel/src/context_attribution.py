from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from control_plane.storage import atomic_write_json, control_data_dir, load_json, project_lock


CONTEXT_ATTRIBUTION_VERSION = "2026-08-30.context-attribution.v1"
ContextCategory = Literal[
    "global_instructions",
    "role_instructions",
    "mode_instructions",
    "runtime_instructions",
    "requirements_context",
    "tasks_context",
    "memory_context",
    "rules_context",
    "active_workflow_context",
    "session_context",
    "tool_results",
    "specialist_results",
    "other",
]
ContextUnit = Literal["characters", "bytes", "tokens", "provider_context_units"]
EvidenceClass = Literal["attributable", "derived", "experimental", "unavailable"]
Completeness = Literal["complete_model_context", "partial_os_contribution", "unknown_host_context"]

CONTEXT_CATEGORIES: tuple[ContextCategory, ...] = (
    "global_instructions",
    "role_instructions",
    "mode_instructions",
    "runtime_instructions",
    "requirements_context",
    "tasks_context",
    "memory_context",
    "rules_context",
    "active_workflow_context",
    "session_context",
    "tool_results",
    "specialist_results",
    "other",
)

_CATEGORY_KEYS: dict[str, ContextCategory] = {
    "requirements": "requirements_context",
    "requirement": "requirements_context",
    "requirement_context": "requirements_context",
    "tasks": "tasks_context",
    "task_context": "tasks_context",
    "memory": "memory_context",
    "project_memory": "memory_context",
    "rules": "rules_context",
    "project_rules": "rules_context",
    "active_workflow": "active_workflow_context",
    "workflow_state": "active_workflow_context",
    "specialist_results": "specialist_results",
    "specialist_result": "specialist_results",
}


class AttributionModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ContextContribution(AttributionModel):
    contribution_id: str = Field(min_length=1)
    category: ContextCategory
    value: int | None = Field(default=None, ge=0)
    unit: ContextUnit
    evidence_class: EvidenceClass
    source: str = ""
    attribution_version: str = CONTEXT_ATTRIBUTION_VERSION
    adapter_version: str = ""
    source_schema_version: str = ""
    completeness: Completeness = "partial_os_contribution"
    privacy_classification: Literal["aggregate_size", "unavailable"] = "aggregate_size"
    content_sha256: str = ""
    workflow_identity: dict[str, str] = Field(default_factory=dict)
    truncated: bool = False
    limitation: str = ""
    observed_at: str = ""

    @model_validator(mode="after")
    def validate_boundary(self) -> "ContextContribution":
        self.workflow_identity = {
            str(key).strip(): str(value).strip()
            for key, value in self.workflow_identity.items()
            if str(key).strip() and str(value).strip()
        }
        if self.evidence_class == "unavailable":
            if self.value is not None or self.privacy_classification != "unavailable":
                raise ValueError("Unavailable context evidence cannot carry a measured value")
            if not self.limitation.strip():
                raise ValueError("Unavailable context evidence requires a limitation")
            if self.content_sha256:
                raise ValueError("Unavailable context evidence cannot carry a content hash")
        else:
            if self.value is None or not self.source.strip():
                raise ValueError("Measured context evidence requires a value and source")
            if self.privacy_classification != "aggregate_size":
                raise ValueError("Measured context evidence must remain aggregate-size metadata")
        if self.content_sha256 and not re.fullmatch(r"[0-9a-f]{64}", self.content_sha256):
            raise ValueError("Context content hashes must be lowercase SHA-256 values")
        if self.completeness == "unknown_host_context" and self.evidence_class != "unavailable":
            raise ValueError("Unknown host context must remain unavailable")
        return self


class ContextWindowComparison(AttributionModel):
    compatible: bool
    unit: ContextUnit | None = None
    attribution_version: str = CONTEXT_ATTRIBUTION_VERSION
    baseline_run_ids: list[str] = Field(default_factory=list)
    candidate_run_ids: list[str] = Field(default_factory=list)
    baseline: dict[str, float] = Field(default_factory=dict)
    candidate: dict[str, float] = Field(default_factory=dict)
    changes_percent: dict[str, float | None] = Field(default_factory=dict)
    unavailable_categories: list[str] = Field(default_factory=list)
    incompatibilities: list[str] = Field(default_factory=list)


class ContextCapabilityAssessment(AttributionModel):
    category: ContextCategory
    evidence_class: EvidenceClass
    source: str = ""
    unit: ContextUnit | None = None
    completeness: Completeness
    availability: Literal["available", "available_when_supplied", "unavailable"]
    privacy_classification: Literal["aggregate_size", "unavailable"]
    limitation: str = ""


class ContextAttributionCapabilityReport(AttributionModel):
    attribution_version: str = CONTEXT_ATTRIBUTION_VERSION
    execution_backend: str
    assessments: list[ContextCapabilityAssessment]


def _stable_id(prefix: str, *parts: object) -> str:
    digest = sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}-{digest}"


def _safe_serialization(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def measured_contribution(
    category: ContextCategory,
    value: object,
    *,
    source: str,
    unit: Literal["characters", "bytes"] = "characters",
    evidence_class: Literal["attributable", "derived", "experimental"] = "attributable",
    workflow_identity: dict[str, str] | None = None,
    adapter_version: str = "",
    source_schema_version: str = "",
    truncated: bool = False,
    observed_at: str = "",
) -> ContextContribution:
    serialized = value if isinstance(value, str) else _safe_serialization(value)
    encoded = serialized.encode("utf-8")
    amount = len(serialized) if unit == "characters" else len(encoded)
    digest = sha256(encoded).hexdigest()
    identity = workflow_identity or {}
    contribution_id = _stable_id(
        "context", CONTEXT_ATTRIBUTION_VERSION, category, source, unit, digest,
        _safe_serialization(identity), truncated,
    )
    return ContextContribution(
        contribution_id=contribution_id,
        category=category,
        value=amount,
        unit=unit,
        evidence_class=evidence_class,
        source=source,
        adapter_version=adapter_version,
        source_schema_version=source_schema_version,
        completeness="partial_os_contribution",
        content_sha256=digest,
        workflow_identity=identity,
        truncated=truncated,
        observed_at=observed_at,
        limitation="This is an OS-controlled contribution measurement, not a complete host-managed model prompt.",
    )


def numeric_contribution(
    category: ContextCategory,
    value: int,
    *,
    unit: ContextUnit,
    source: str,
    evidence_class: Literal["attributable", "derived", "experimental"] = "attributable",
    workflow_identity: dict[str, str] | None = None,
    adapter_version: str = "",
    source_schema_version: str = "",
    truncated: bool = False,
    observed_at: str = "",
    limitation: str = "",
) -> ContextContribution:
    identity = workflow_identity or {}
    return ContextContribution(
        contribution_id=_stable_id(
            "context-numeric", CONTEXT_ATTRIBUTION_VERSION, category, value, unit, source,
            _safe_serialization(identity), truncated,
        ),
        category=category,
        value=value,
        unit=unit,
        evidence_class=evidence_class,
        source=source,
        adapter_version=adapter_version,
        source_schema_version=source_schema_version,
        completeness="partial_os_contribution",
        workflow_identity=identity,
        truncated=truncated,
        observed_at=observed_at,
        limitation=limitation or "This numeric source measures one context contribution, not the complete model prompt.",
    )


def unavailable_host_context(*, workflow_identity: dict[str, str] | None = None) -> ContextContribution:
    identity = workflow_identity or {}
    return ContextContribution(
        contribution_id=_stable_id(
            "context-unavailable", CONTEXT_ATTRIBUTION_VERSION, _safe_serialization(identity)
        ),
        category="other",
        value=None,
        unit="provider_context_units",
        evidence_class="unavailable",
        source="",
        completeness="unknown_host_context",
        privacy_classification="unavailable",
        workflow_identity=identity,
        limitation="Host-managed prompt context is not observable at the AI Builder OS boundary.",
    )


def extract_named_contributions(
    value: object,
    *,
    source: str,
    workflow_identity: dict[str, str] | None = None,
) -> list[ContextContribution]:
    """Measure explicitly named project-context fields without retaining their values."""
    found: list[ContextContribution] = []

    def visit(item: object) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                normalized = str(key).strip().casefold().replace("-", "_")
                category = _CATEGORY_KEYS.get(normalized)
                if category is not None:
                    found.append(measured_contribution(
                        category, child, source=source, workflow_identity=workflow_identity
                    ))
                    continue
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, str):
            candidate = item.strip()
            if candidate.startswith(("{", "[")):
                try:
                    visit(json.loads(candidate))
                except json.JSONDecodeError:
                    return

    visit(value)
    unique = {item.contribution_id: item for item in found}
    return [unique[key] for key in sorted(unique)]


def aggregate_contributions(
    contributions: Iterable[ContextContribution],
    *,
    unit: ContextUnit,
) -> dict[str, float]:
    totals: dict[str, float] = {}
    seen: set[str] = set()
    for item in contributions:
        if item.contribution_id in seen:
            continue
        seen.add(item.contribution_id)
        if item.evidence_class == "unavailable" or item.value is None or item.unit != unit:
            continue
        totals[item.category] = totals.get(item.category, 0.0) + float(item.value)
    return dict(sorted(totals.items()))


def compare_context_windows(
    baseline: dict[str, list[ContextContribution]],
    candidate: dict[str, list[ContextContribution]],
) -> ContextWindowComparison:
    baseline_ids = sorted(baseline)
    candidate_ids = sorted(candidate)
    incompatibilities: list[str] = []
    if not baseline_ids or not candidate_ids:
        incompatibilities.append("Both baseline and candidate require at least one run.")
    all_items = [item for values in (*baseline.values(), *candidate.values()) for item in values]
    versions = {item.attribution_version for item in all_items if item.evidence_class != "unavailable"}
    units = {item.unit for item in all_items if item.evidence_class != "unavailable"}
    if len(versions) > 1:
        incompatibilities.append("Context attribution versions differ across windows.")
    if len(units) > 1:
        incompatibilities.append("Context units differ across windows.")
    if not units:
        incompatibilities.append("No measured context contributions exist in either window.")
    if incompatibilities:
        return ContextWindowComparison(
            compatible=False,
            baseline_run_ids=baseline_ids,
            candidate_run_ids=candidate_ids,
            incompatibilities=incompatibilities,
            unavailable_categories=list(CONTEXT_CATEGORIES),
        )
    unit = next(iter(units))

    def per_run(window: dict[str, list[ContextContribution]]) -> dict[str, float]:
        category_values: dict[str, list[float]] = {}
        for items in window.values():
            totals = aggregate_contributions(items, unit=unit)
            for category in CONTEXT_CATEGORIES:
                if category in totals:
                    category_values.setdefault(category, []).append(totals[category])
        return {
            category: sum(values) / len(values)
            for category, values in sorted(category_values.items())
            if values
        }

    baseline_values = per_run(baseline)
    candidate_values = per_run(candidate)
    categories = sorted(set(baseline_values) | set(candidate_values))
    changes: dict[str, float | None] = {}
    for category in categories:
        before = baseline_values.get(category)
        after = candidate_values.get(category)
        changes[category] = (
            None if before in {None, 0} or after is None else ((after - before) / before) * 100
        )
    return ContextWindowComparison(
        compatible=True,
        unit=unit,
        baseline_run_ids=baseline_ids,
        candidate_run_ids=candidate_ids,
        baseline=baseline_values,
        candidate=candidate_values,
        changes_percent=changes,
        unavailable_categories=[item for item in CONTEXT_CATEGORIES if item not in categories],
    )


def context_attribution_capability_report(execution_backend: str) -> ContextAttributionCapabilityReport:
    sdk = execution_backend == "openai_agents_sdk"
    sdk_direct = {
        "global_instructions", "role_instructions", "mode_instructions", "runtime_instructions",
        "session_context", "tool_results",
    }
    named_project = {
        "requirements_context", "tasks_context", "memory_context", "rules_context",
        "active_workflow_context", "specialist_results",
    }
    assessments: list[ContextCapabilityAssessment] = []
    for category in CONTEXT_CATEGORIES:
        if sdk and category in sdk_direct:
            assessments.append(ContextCapabilityAssessment(
                category=category,
                evidence_class="attributable",
                source="agents_sdk_prompt_and_tool_hooks",
                unit="characters",
                completeness="partial_os_contribution",
                availability="available",
                privacy_classification="aggregate_size",
                limitation="The SDK boundary measures this supplied component; provider-added prompt material remains outside this category.",
            ))
        elif category in named_project:
            assessments.append(ContextCapabilityAssessment(
                category=category,
                evidence_class="attributable",
                source="named_os_context_fields",
                unit="characters",
                completeness="partial_os_contribution",
                availability="available_when_supplied",
                privacy_classification="aggregate_size",
                limitation="Available only when the OS supplies a deterministically named context field.",
            ))
        elif not sdk and category == "tool_results":
            assessments.append(ContextCapabilityAssessment(
                category=category,
                evidence_class="attributable",
                source="ai_builder_os_mcp_return_or_codex_otel",
                unit="bytes",
                completeness="partial_os_contribution",
                availability="available_when_supplied",
                privacy_classification="aggregate_size",
                limitation="Measures OS return payloads or source-reported results, not whether the Codex host retained them in its prompt.",
            ))
        else:
            assessments.append(ContextCapabilityAssessment(
                category=category,
                evidence_class="unavailable",
                completeness="unknown_host_context",
                availability="unavailable",
                privacy_classification="unavailable",
                limitation="This context category is managed by the Codex host and is not observable at the OS boundary.",
            ))
    return ContextAttributionCapabilityReport(
        execution_backend=execution_backend,
        assessments=assessments,
    )


class ContextAttributionStore:
    def __init__(self, project_name: str) -> None:
        self.project_name = project_name
        self.path: Path = control_data_dir(project_name) / "system_learning" / "context_contributions.json"

    def records(self) -> list[ContextContribution]:
        raw = load_json(self.path, [])
        return [ContextContribution.model_validate(item) for item in raw] if isinstance(raw, list) else []

    def record(self, contribution: ContextContribution) -> bool:
        with project_lock(self.project_name):
            records = self.records()
            existing = next(
                (item for item in records if item.contribution_id == contribution.contribution_id), None
            )
            if existing is not None:
                if existing.model_dump(mode="json") != contribution.model_dump(mode="json"):
                    raise ValueError("Immutable context contribution identity conflict")
                return False
            records.append(contribution)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_json(self.path, [item.model_dump(mode="json") for item in records])
            return True

    def for_run_ids(self, run_ids: Iterable[str]) -> list[ContextContribution]:
        wanted = {item for item in run_ids if item}
        return [
            item for item in self.records()
            if wanted.intersection({
                item.workflow_identity.get("run_id", ""),
                item.workflow_identity.get("trace_id", ""),
                item.workflow_identity.get("work_request_id", ""),
            })
        ]


def record_mcp_result_contribution(
    project_name: str,
    tool_name: str,
    result: object,
    *,
    workflow_identity: dict[str, str] | None = None,
) -> None:
    """Best-effort MCP return-value measurement; telemetry cannot affect the tool result."""
    serialized = _safe_serialization(result)
    identity = {"project_name": project_name, "tool_name": tool_name, **(workflow_identity or {})}
    observed_at = datetime.now(timezone.utc).isoformat()
    contribution = measured_contribution(
        "tool_results",
        serialized,
        source=f"ai_builder_os_mcp_return:{tool_name}",
        unit="bytes",
        evidence_class="attributable",
        workflow_identity=identity,
        adapter_version=CONTEXT_ATTRIBUTION_VERSION,
        source_schema_version="mcp-python-return-json.v1",
        truncated=serialized.endswith("...[truncated]"),
        observed_at=observed_at,
    )
    # Calls with identical privacy-safe output may still be distinct contributions. The
    # timestamp is added only to identity, never to retained source content.
    contribution = contribution.model_copy(update={
        "contribution_id": _stable_id("context-mcp", contribution.contribution_id, observed_at)
    })
    store = ContextAttributionStore(project_name)
    store.record(contribution)
    for named in extract_named_contributions(
        result,
        source=f"ai_builder_os_mcp_named_context:{tool_name}",
        workflow_identity=identity,
    ):
        store.record(named)
