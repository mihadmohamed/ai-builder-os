from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class WorkflowDecision:
    project_name: str
    next_action: str
    next_role: str
    why: str
    blocking_approval_ids: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class WorkPacket:
    run_id: str
    lease_token: str
    project_name: str
    requirement_id: str
    executor: str
    status: str
    claimed_at: str
    expires_at: str
    requirement: dict[str, Any]
    product_files: dict[str, str]
    instructions: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CodexWorkRequest:
    request_id: str
    project_name: str
    task: str
    requested_role: str
    requirement_id: str
    status: str
    requested_by: str
    source: str
    created_at: str
    claimed_by: str = ""
    claimed_at: str = ""
    claim_expires_at: str = ""
    resolved_at: str = ""
    summary: str = ""
    implementation_run_id: str = ""
    request_kind: str = "general"
    payload: dict[str, Any] = field(default_factory=dict)
    result_proposal_id: str = ""
    result_proposal_revision: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PMProposalRecord:
    proposal_id: str
    proposal_revision: int
    project_name: str
    status: str
    actor: str
    source: str
    submitted_at: str
    proposal: dict[str, Any]
    idempotency_key: str = ""
    resolved_at: str = ""
    resolved_by: str = ""
    resolution_source: str = ""
    rejection_reason: str = ""
    origin_request_id: str = ""
    parent_proposal_id: str = ""
    parent_proposal_revision: int = 0
    origin_sdk_run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
