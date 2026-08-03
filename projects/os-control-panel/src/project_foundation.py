from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import NAMESPACE_URL, uuid4, uuid5

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


FoundationFieldName = Literal[
    "project_objectives",
    "target_audience",
    "business_goal",
    "scope",
    "constraints",
    "priority_journeys",
    "success_metrics",
]
FoundationProvenance = Literal[
    "missing",
    "user_provided",
    "research_accepted",
    "assumption_accepted",
    "not_applicable",
]

FOUNDATION_FIELD_ORDER: tuple[FoundationFieldName, ...] = (
    "project_objectives",
    "target_audience",
    "business_goal",
    "scope",
    "constraints",
    "priority_journeys",
    "success_metrics",
)
FOUNDATION_FIELD_LABELS: dict[FoundationFieldName, str] = {
    "project_objectives": "project objectives",
    "target_audience": "target audience",
    "business_goal": "business goal",
    "scope": "first-release scope and exclusions",
    "constraints": "constraints",
    "priority_journeys": "priority user journeys",
    "success_metrics": "success metrics",
}
FOUNDATION_QUESTIONS: dict[FoundationFieldName, str] = {
    "project_objectives": "What outcomes should this project achieve?",
    "target_audience": "Who is the primary audience, and whose needs matter most first?",
    "business_goal": "What business result or strategic goal should this project support?",
    "scope": "What must the first release include, and what should it deliberately exclude?",
    "constraints": "What constraints or non-negotiable boundaries must the project respect?",
    "priority_journeys": "Which user journeys must work especially well in the first release?",
    "success_metrics": "What observable metrics or evidence will show that the project is succeeding?",
}


class FoundationModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ResearchEvidence(FoundationModel):
    url: str
    title: str
    observed_at: str

    @field_validator("url")
    @classmethod
    def validate_safe_source_url(cls, value: str) -> str:
        normalized = value.strip()
        if not re.match(r"^https?://[^\s]+$", normalized, flags=re.IGNORECASE):
            raise ValueError("Research evidence requires an HTTP(S) source URL")
        return normalized

    @field_validator("title", "observed_at")
    @classmethod
    def validate_evidence_metadata(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Research evidence metadata must not be empty")
        return normalized


class ResearchOption(FoundationModel):
    option_id: str = Field(default_factory=lambda: str(uuid4()))
    label: str
    value: str
    tradeoffs: list[str] = Field(default_factory=list, max_length=6)
    confidence: Literal["low", "medium", "high", "unknown"] = "unknown"
    recommended: bool = False
    remaining_uncertainty: str = ""
    evidence: list[ResearchEvidence] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_attribution(self) -> "ResearchOption":
        if not self.value.strip() or not self.label.strip():
            raise ValueError("Research options require a label and substantive value")
        if not self.evidence:
            raise ValueError("Research options require attributable source evidence")
        return self


class FoundationField(FoundationModel):
    value: str = ""
    provenance: FoundationProvenance = "missing"
    rationale: str = ""
    confidence: Literal["", "low", "medium", "high", "unknown"] = ""
    evidence: list[ResearchEvidence] = Field(default_factory=list, max_length=8)

    @model_validator(mode="after")
    def validate_state(self) -> "FoundationField":
        self.value = self.value.strip()
        self.rationale = self.rationale.strip()
        if self.provenance == "missing":
            if self.value or self.evidence:
                raise ValueError("Missing fields cannot carry accepted values or evidence")
        elif self.provenance == "not_applicable":
            if not self.rationale:
                raise ValueError("Not-applicable fields require a rationale")
        elif not self.value:
            raise ValueError("Completed foundation fields require a value")
        if self.provenance == "research_accepted" and not self.evidence:
            raise ValueError("Research-backed fields require source evidence")
        return self

    @property
    def complete(self) -> bool:
        return self.provenance != "missing"


class ProjectIdentity(FoundationModel):
    project_name: str
    display_name: str
    ui_runtime: Literal["streamlit", "web_app"] = "streamlit"
    repository_destination: Literal["standalone", "embedded_showcase"] = "standalone"
    visibility: Literal["private", "public"] = "private"
    ownership: Literal["self", "client", "organisation"] = "self"
    repository: str = ""
    organisation_or_client_boundary: str = ""


class ProjectFoundation(FoundationModel):
    schema_version: Literal["2026-08-03.project-foundation.v1"] = "2026-08-03.project-foundation.v1"
    foundation_id: str = Field(default_factory=lambda: str(uuid4()))
    identity: ProjectIdentity
    project_objectives: FoundationField = Field(default_factory=FoundationField)
    target_audience: FoundationField = Field(default_factory=FoundationField)
    business_goal: FoundationField = Field(default_factory=FoundationField)
    scope: FoundationField = Field(default_factory=FoundationField)
    constraints: FoundationField = Field(default_factory=FoundationField)
    priority_journeys: FoundationField = Field(default_factory=FoundationField)
    success_metrics: FoundationField = Field(default_factory=FoundationField)
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def missing_fields(self) -> list[FoundationFieldName]:
        return [name for name in FOUNDATION_FIELD_ORDER if not getattr(self, name).complete]

    def next_gap(self) -> FoundationFieldName | None:
        missing = self.missing_fields()
        return missing[0] if missing else None

    def next_question(self) -> str:
        gap = self.next_gap()
        return FOUNDATION_QUESTIONS[gap] if gap else ""

    @property
    def complete(self) -> bool:
        return not self.missing_fields()

    def accept_user_answer(self, field: FoundationFieldName, value: str) -> "ProjectFoundation":
        return self.model_copy(
            update={
                field: FoundationField(value=value, provenance="user_provided", confidence="high"),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def accept_research_option(self, field: FoundationFieldName, option: ResearchOption) -> "ProjectFoundation":
        return self.model_copy(
            update={
                field: FoundationField(
                    value=option.value,
                    provenance="research_accepted",
                    confidence=option.confidence,
                    evidence=option.evidence,
                    rationale=option.remaining_uncertainty,
                ),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def accept_assumption(self, field: FoundationFieldName, value: str, rationale: str) -> "ProjectFoundation":
        if not rationale.strip():
            raise ValueError("Accepted assumptions require a rationale")
        return self.model_copy(
            update={
                field: FoundationField(
                    value=value,
                    provenance="assumption_accepted",
                    confidence="low",
                    rationale=rationale,
                ),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def mark_not_applicable(self, field: FoundationFieldName, rationale: str) -> "ProjectFoundation":
        return self.model_copy(
            update={
                field: FoundationField(provenance="not_applicable", rationale=rationale),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def source_sha256(self) -> str:
        payload = self.model_dump(mode="json", exclude={"updated_at"})
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()


class PreProjectProposal(FoundationModel):
    proposal_id: str = Field(default_factory=lambda: str(uuid4()))
    revision: int = 1
    status: Literal["PENDING_APPROVAL", "APPROVED", "REJECTED"] = "PENDING_APPROVAL"
    foundation: ProjectFoundation
    initial_requirement_title: str
    initial_requirement: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: str = ""
    resolved_by: str = ""
    foundation_sha256: str = ""
    seal: str = ""

    @model_validator(mode="after")
    def validate_proposal(self) -> "PreProjectProposal":
        if not self.foundation.complete:
            raise ValueError(f"Project foundation is incomplete: {', '.join(self.foundation.missing_fields())}")
        if not self.initial_requirement_title.strip() or not self.initial_requirement.strip():
            raise ValueError("Pre-project proposals require one grounded initial requirement")
        current_sha256 = self.foundation.source_sha256()
        if self.foundation_sha256 and self.foundation_sha256 != current_sha256:
            raise ValueError("Pre-project proposal foundation fingerprint is stale")
        self.foundation_sha256 = current_sha256
        if not self.seal:
            payload = self.model_dump(mode="json", exclude={"seal", "status", "resolved_at", "resolved_by"})
            self.seal = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
        return self

    def approve(self, *, exact_seal: str, actor: str, current_foundation: ProjectFoundation) -> "PreProjectProposal":
        if self.status != "PENDING_APPROVAL":
            raise ValueError("Pre-project proposal is already resolved")
        if exact_seal != self.seal:
            raise ValueError("Exact pre-project proposal seal does not match")
        if current_foundation.source_sha256() != self.foundation_sha256:
            raise ValueError("Pre-project proposal is stale because the foundation changed")
        return self.model_copy(
            update={
                "status": "APPROVED",
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "resolved_by": actor.strip() or "product-director",
            }
        )

    def reject(self, *, exact_seal: str, actor: str) -> "PreProjectProposal":
        if self.status != "PENDING_APPROVAL":
            raise ValueError("Pre-project proposal is already resolved")
        if exact_seal != self.seal:
            raise ValueError("Exact pre-project proposal seal does not match")
        return self.model_copy(
            update={
                "status": "REJECTED",
                "resolved_at": datetime.now(timezone.utc).isoformat(),
                "resolved_by": actor.strip() or "product-director",
            }
        )


class ProjectDiscoverySession(FoundationModel):
    schema_version: Literal["2026-08-03.project-discovery.v1"] = "2026-08-03.project-discovery.v1"
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    execution_backend: Literal["codex_native", "openai_api"] = "codex_native"
    status: Literal["DISCOVERING", "PENDING_APPROVAL", "APPROVED", "REJECTED"] = "DISCOVERING"
    foundation: ProjectFoundation
    research_options: dict[FoundationFieldName, list[ResearchOption]] = Field(default_factory=dict)
    proposal: PreProjectProposal | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def next_gap(self) -> FoundationFieldName | None:
        return self.foundation.next_gap()

    def with_foundation(self, foundation: ProjectFoundation) -> "ProjectDiscoverySession":
        if self.status in {"APPROVED", "REJECTED"}:
            raise ValueError("Resolved discovery sessions are immutable")
        return self.model_copy(
            update={
                "foundation": foundation,
                "status": "DISCOVERING",
                "proposal": None,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def offer_research(self, field: FoundationFieldName, options: list[ResearchOption]) -> "ProjectDiscoverySession":
        if field != self.next_gap:
            raise ValueError("Research options must resolve the current foundation gap")
        if not 2 <= len(options) <= 3:
            raise ValueError("Research must return two or three distinct options")
        if len({option.value.strip().casefold() for option in options}) != len(options):
            raise ValueError("Research options must be distinct")
        choices = dict(self.research_options)
        choices[field] = options
        return self.model_copy(
            update={"research_options": choices, "updated_at": datetime.now(timezone.utc).isoformat()}
        )

    def select_research(self, field: FoundationFieldName, option_id: str) -> "ProjectDiscoverySession":
        option = next(
            (candidate for candidate in self.research_options.get(field, []) if candidate.option_id == option_id),
            None,
        )
        if option is None:
            raise ValueError("Unknown research option")
        return self.with_foundation(self.foundation.accept_research_option(field, option))

    def prepare_proposal(self, *, revision: int = 1) -> "ProjectDiscoverySession":
        title, requirement = derive_initial_requirement(self.foundation)
        proposal = PreProjectProposal(
            revision=revision,
            foundation=self.foundation,
            initial_requirement_title=title,
            initial_requirement=requirement,
        )
        return self.model_copy(
            update={
                "status": "PENDING_APPROVAL",
                "proposal": proposal,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    def approve(self, *, exact_seal: str, actor: str) -> "ProjectDiscoverySession":
        if self.proposal is None:
            raise ValueError("No pre-project proposal is pending")
        approved = self.proposal.approve(
            exact_seal=exact_seal,
            actor=actor,
            current_foundation=self.foundation,
        )
        return self.model_copy(
            update={
                "status": "APPROVED",
                "proposal": approved,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )


def save_discovery_session(path: Path, session: ProjectDiscoverySession) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(
        json.dumps(session.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def load_discovery_session(path: Path) -> ProjectDiscoverySession | None:
    if not path.exists():
        return None
    return ProjectDiscoverySession.model_validate_json(path.read_text(encoding="utf-8"))


def derive_initial_requirement(foundation: ProjectFoundation) -> tuple[str, str]:
    if not foundation.complete:
        raise ValueError(f"Project foundation is incomplete: {', '.join(foundation.missing_fields())}")
    title = f"Deliver the first {foundation.identity.display_name} journey"
    description = "\n".join(
        [
            "Project foundation:",
            f"- Foundation ID: {foundation.foundation_id}",
            "",
            "Problem statement:",
            foundation.business_goal.value,
            "",
            "Target user:",
            foundation.target_audience.value,
            "",
            "Core job-to-be-done:",
            foundation.priority_journeys.value,
            "",
            "Desired outcome:",
            foundation.project_objectives.value,
            "",
            "Success and acceptance evidence:",
            foundation.success_metrics.value,
            "",
            "Constraints:",
            foundation.constraints.value,
            "",
            "Out of scope:",
            foundation.scope.value,
            "",
            "Assumptions:",
            "- Project-level context is governed by the referenced foundation and is not duplicated here.",
            "",
            "Open questions:",
            "- None.",
        ]
    )
    return title, description


def foundation_from_markdown(identity: ProjectIdentity, markdown: str) -> ProjectFoundation:
    aliases: dict[FoundationFieldName, tuple[str, ...]] = {
        "project_objectives": ("Project objectives", "Desired outcome"),
        "target_audience": ("Target audience", "Target user"),
        "business_goal": ("Business goal", "Problem statement"),
        "scope": ("Scope", "Out of scope"),
        "constraints": ("Constraints",),
        "priority_journeys": ("Priority journeys", "Core job-to-be-done"),
        "success_metrics": ("Success metrics", "Success and acceptance evidence", "Success criteria"),
    }
    headings = [item for values in aliases.values() for item in values]
    pattern = re.compile(
        rf"(?ms)^({'|'.join(re.escape(item) for item in headings)}):?\s*$\n(.*?)(?=^(?:{'|'.join(re.escape(item) for item in headings)}):?\s*$|\Z)"
    )
    sections = {match.group(1): match.group(2).strip() for match in pattern.finditer(markdown.strip())}
    updates: dict[str, object] = {
        "identity": identity,
        "foundation_id": str(uuid5(NAMESPACE_URL, f"ai-builder-os:{identity.project_name}:{markdown.strip()}")),
    }
    for field, labels in aliases.items():
        value = next((sections[label] for label in labels if sections.get(label)), "")
        updates[field] = (
            FoundationField(value=value, provenance="user_provided", confidence="medium")
            if value
            else FoundationField()
        )
    return ProjectFoundation.model_validate(updates)
