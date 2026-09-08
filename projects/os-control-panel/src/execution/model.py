from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Protocol, Sequence


class ExecutorTier(str, Enum):
    DETERMINISTIC = "deterministic"
    LOCAL = "local"
    LUNA = "luna"
    TERRA = "terra"
    SOL = "sol"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskType(str, Enum):
    TRANSFORM = "transform"
    CLASSIFICATION = "classification"
    REVIEW = "review"
    REPOSITORY = "repository"
    IMPLEMENTATION = "implementation"
    APPROVAL = "approval"
    CANONICAL_STATE = "canonical_state"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Availability:
    available: bool
    observed_at: str
    reason: str = ""


@dataclass(frozen=True)
class ExecutorDescriptor:
    tier: ExecutorTier
    identity: str
    capabilities: frozenset[str] = frozenset()
    relative_cost: str = ""
    reasoning: str = ""


@dataclass(frozen=True)
class ExecutionRequest:
    project_id: str
    requirement_id: str
    task_id: str
    task_type: TaskType
    risk: RiskLevel
    required_capabilities: frozenset[str] = frozenset()
    context_bytes: int = 0
    # This is an ephemeral, manager-owned input only.  It must never be copied
    # to an attempt, result record, controller history, or adapter trace.
    context: str = ""
    schema_required: bool = False
    tools_requested: frozenset[str] = frozenset()
    approved_override_tier: ExecutorTier | None = None
    override_reason: str = ""


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    executor: ExecutorDescriptor
    output: object | None = None
    validation_passed: bool = False
    safe_error: str = ""
    escalation_reason: str = ""
    duration_ms: int = 0
    confidence: str = ""


@dataclass(frozen=True)
class ExecutionAttempt:
    tier: ExecutorTier
    status: str
    reason: str
    duration_ms: int = 0
    validation_passed: bool = False


@dataclass(frozen=True)
class ExecutionPolicy:
    version: str = "r120-observation-v1"
    tier_order: tuple[ExecutorTier, ...] = (
        ExecutorTier.DETERMINISTIC, ExecutorTier.LOCAL, ExecutorTier.LUNA,
        ExecutorTier.TERRA, ExecutorTier.SOL,
    )
    automatic_routing: bool = False
    local_context_default: int = 8192
    local_context_max: int = 16384
    max_same_tier_corrections: int = 1
    allowed_tools: frozenset[str] = frozenset()
    local_eligible_types: frozenset[TaskType] = frozenset()


class Executor(Protocol):
    descriptor: ExecutorDescriptor

    def availability(self, request: ExecutionRequest) -> Availability: ...
    def execute(self, request: ExecutionRequest) -> ExecutionResult: ...
