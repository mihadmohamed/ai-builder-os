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

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
