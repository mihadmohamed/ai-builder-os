"""Governed, provider-neutral execution primitives for R120.

This package deliberately contains no controller, queue, claim, or history
mutations.  Those remain owned by ``control_plane``.
"""

from .manager import CuratedContext, ExecutionManager, InMemoryAttemptStore, curate_context
from .adapters import CodexExecutor, DeterministicWorker, LocalModelExecutor
from .model import (
    Availability,
    ExecutionAttempt,
    ExecutionPolicy,
    ExecutionRequest,
    ExecutionResult,
    ExecutorDescriptor,
    ExecutorTier,
    RiskLevel,
    TaskType,
)

__all__ = [
    "Availability", "ExecutionAttempt", "ExecutionManager", "ExecutionPolicy",
    "ExecutionRequest", "ExecutionResult", "ExecutorDescriptor", "ExecutorTier",
    "InMemoryAttemptStore", "CuratedContext", "curate_context", "RiskLevel", "TaskType",
    "CodexExecutor", "DeterministicWorker", "LocalModelExecutor",
]
