from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import re
from typing import Iterable

from .model import Availability, ExecutionAttempt, ExecutionPolicy, ExecutionRequest, ExecutionResult, Executor, ExecutorTier, RiskLevel, TaskType


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*)(?:bearer\s+)?[^\s,;]+"),
    re.compile(r"(?i)(api[_-]?key\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"\bsk-[A-Za-z0-9_-]+"),
)


@dataclass(frozen=True)
class CuratedContext:
    """Ephemeral local context.  Only the aggregate fields may be observed."""
    text: str
    bytes: int
    redactions: int


def curate_context(text: str, limit: int) -> CuratedContext:
    """Redact then bound caller context before it could reach a local adapter."""
    redactions = 0
    for pattern in _SECRET_PATTERNS:
        text, count = pattern.subn(lambda match: f"{match.group(1)}[REDACTED]" if match.lastindex else "[REDACTED]", text)
        redactions += count
    encoded = text.encode("utf-8")[:limit]
    # Ignore incomplete trailing UTF-8 rather than accidentally exceeding the
    # manager's stated byte boundary.
    bounded = encoded.decode("utf-8", errors="ignore")
    return CuratedContext(bounded, len(bounded.encode("utf-8")), redactions)


@dataclass
class InMemoryAttemptStore:
    attempts: list[ExecutionAttempt] = field(default_factory=list)
    def append(self, attempt: ExecutionAttempt) -> None:
        self.attempts.append(attempt)


class ExecutionManager:
    """Selection and bounded escalation only; never an authority boundary."""
    def __init__(self, executors: Iterable[Executor], policy: ExecutionPolicy, store: InMemoryAttemptStore | None = None):
        self.executors = {item.descriptor.tier: item for item in executors}
        self.policy, self.store = policy, store or InMemoryAttemptStore()

    def curated_context(self, request: ExecutionRequest) -> CuratedContext:
        return curate_context(request.context, self.policy.local_context_max)

    def _context_bytes(self, request: ExecutionRequest) -> int:
        return len(request.context.encode("utf-8")) if request.context else request.context_bytes

    def eligible_tiers(self, request: ExecutionRequest) -> tuple[ExecutorTier, ...]:
        if request.tools_requested - self.policy.allowed_tools:
            return ()
        if request.risk is RiskLevel.HIGH or request.task_type in {TaskType.APPROVAL, TaskType.IMPLEMENTATION, TaskType.REPOSITORY}:
            return tuple(t for t in self.policy.tier_order if t in {ExecutorTier.LUNA, ExecutorTier.TERRA, ExecutorTier.SOL})
        tiers = self.policy.tier_order
        if request.task_type not in self.policy.local_eligible_types:
            tiers = tuple(t for t in tiers if t is not ExecutorTier.LOCAL)
        if self._context_bytes(request) > self.policy.local_context_max:
            tiers = tuple(t for t in tiers if t is not ExecutorTier.LOCAL)
        # Tool work has no safe, governed local adapter in V1.  Allow-listing
        # only says a controller may grant the tool; it never grants it to the
        # local model.
        if request.tools_requested:
            tiers = tuple(t for t in tiers if t is not ExecutorTier.LOCAL)
        if request.approved_override_tier:
            if not request.override_reason or request.approved_override_tier not in tiers:
                return ()
            return tuple(t for t in tiers if t == request.approved_override_tier)
        return tiers

    def route(self, request: ExecutionRequest) -> ExecutionResult:
        tiers = self.eligible_tiers(request)
        if not tiers:
            return self._failed(request, "POLICY_BLOCKED")
        selected = next((tier for tier in tiers if tier in self.executors and self.executors[tier].availability(request).available), None)
        if selected is None:
            return self._waiting(request, "WAITING_FOR_EXECUTOR")
        executor = self.executors[selected]
        if selected is ExecutorTier.LOCAL:
            context = self.curated_context(request)
            self.store.append(ExecutionAttempt(selected, "SHADOW", "OBSERVATION_MODE"))
            return ExecutionResult(
                "SHADOW", executor.descriptor,
                output={"context_bytes": context.bytes, "redactions": context.redactions},
                escalation_reason="OBSERVATION_MODE",
            )
        if not self.policy.automatic_routing and selected is ExecutorTier.DETERMINISTIC:
            self.store.append(ExecutionAttempt(selected, "SHADOW", "OBSERVATION_MODE"))
            return ExecutionResult("SHADOW", executor.descriptor, escalation_reason="OBSERVATION_MODE")
        result = executor.execute(request)
        self.store.append(ExecutionAttempt(selected, result.status, result.escalation_reason or result.safe_error, result.duration_ms, result.validation_passed))
        if result.status == "SUCCESS" or result.validation_passed:
            return result
        if not result.escalation_reason:
            return result
        return self._escalate(request, tiers, selected, result.escalation_reason)

    def _escalate(self, request: ExecutionRequest, tiers: tuple[ExecutorTier, ...], current: ExecutorTier, reason: str) -> ExecutionResult:
        after = tiers[tiers.index(current) + 1:]
        next_tier = next((tier for tier in after if tier in self.executors and self.executors[tier].availability(request).available), None)
        if next_tier is None:
            return self._waiting(request, reason)
        result = self.executors[next_tier].execute(request)
        self.store.append(ExecutionAttempt(next_tier, result.status, reason, result.duration_ms, result.validation_passed))
        return result

    def _waiting(self, request: ExecutionRequest, reason: str) -> ExecutionResult:
        executor = next(iter(self.executors.values()), None)
        if executor is None:
            raise ValueError("ExecutionManager requires at least one executor")
        return ExecutionResult("WAITING_FOR_EXECUTOR", executor.descriptor, escalation_reason=reason)

    def _failed(self, request: ExecutionRequest, reason: str) -> ExecutionResult:
        executor = next(iter(self.executors.values()), None)
        if executor is None:
            raise ValueError("ExecutionManager requires at least one executor")
        return ExecutionResult("FAILED", executor.descriptor, safe_error=reason)
