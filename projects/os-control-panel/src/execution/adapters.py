from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlsplit
from urllib.error import URLError
from urllib.request import Request, urlopen

from .model import Availability, ExecutionRequest, ExecutionResult, ExecutorDescriptor, ExecutorTier


@dataclass
class DeterministicWorker:
    """Explicit, fixed transforms only; no model or tool authority."""
    transforms: dict[str, callable]
    allowed_task_ids: frozenset[str] = frozenset()
    descriptor: ExecutorDescriptor = ExecutorDescriptor(ExecutorTier.DETERMINISTIC, "deterministic-worker")
    def availability(self, request: ExecutionRequest) -> Availability:
        return Availability(request.task_id in self.allowed_task_ids and request.task_id in self.transforms, "")
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        transform = self.transforms.get(request.task_id) if request.task_id in self.allowed_task_ids else None
        if transform is None:
            return ExecutionResult("FAILED", self.descriptor, safe_error="UNSUPPORTED_DETERMINISTIC_TASK")
        try:
            return ExecutionResult("SUCCESS", self.descriptor, output=transform(), validation_passed=True)
        except Exception:
            return ExecutionResult("FAILED", self.descriptor, safe_error="DETERMINISTIC_TRANSFORM_FAILED")


@dataclass
class LocalModelExecutor:
    """Loopback-only Ollama adapter. Callers keep it in shadow mode initially."""
    model: str = "qwen3.5:9b-q4_K_M"
    endpoint: str = "http://127.0.0.1:11434"
    descriptor: ExecutorDescriptor = ExecutorDescriptor(ExecutorTier.LOCAL, "ollama:qwen3.5:9b-q4_K_M", frozenset({"structured"}), "local")
    def __post_init__(self):
        parsed = urlsplit(self.endpoint)
        if (parsed.scheme, parsed.hostname, parsed.port, parsed.username, parsed.password, parsed.path, parsed.query, parsed.fragment) != ("http", "127.0.0.1", 11434, None, None, "", "", ""):
            raise ValueError("LocalModelExecutor only permits loopback Ollama endpoints")
    def availability(self, request: ExecutionRequest) -> Availability:
        try:
            with urlopen(Request(f"{self.endpoint}/api/tags", method="GET"), timeout=2) as response:
                payload = json.loads(response.read(128_000))
            names = {str(item.get("name", "")) for item in payload.get("models", []) if isinstance(item, dict)}
            return Availability(self.model in names, "", "MODEL_UNAVAILABLE" if self.model not in names else "")
        except (URLError, OSError, ValueError, json.JSONDecodeError):
            return Availability(False, "", "OLLAMA_UNAVAILABLE")
    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult("FAILED", self.descriptor, safe_error="LOCAL_EXECUTION_REQUIRES_APPROVED_PROMPT_ADAPTER")


@dataclass
class CodexExecutor:
    """Adapter boundary for the existing managed Codex worker.

    The worker still owns CLI invocation and controller claim handling; this
    adapter exposes only availability and typed tier identity to routing policy.
    """
    tier: ExecutorTier = ExecutorTier.LUNA
    availability_check: Callable[[ExecutionRequest], Availability] | None = None
    execute_callback: Callable[[ExecutionRequest], ExecutionResult] | None = None

    @property
    def descriptor(self) -> ExecutorDescriptor:
        reasoning = "medium" if self.tier is ExecutorTier.SOL else ""
        return ExecutorDescriptor(self.tier, f"codex:{self.tier.value}", frozenset({"repository", "review"}), "codex", reasoning)

    def availability(self, request: ExecutionRequest) -> Availability:
        if self.availability_check is None:
            return Availability(True, "", "UNOBSERVED")
        return self.availability_check(request)

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        # The controller-owned worker supplies this callback only after it has
        # validated managed-handoff lineage and acquired a fresh claim.  The
        # adapter itself intentionally cannot create work or mutate controller
        # state.
        if self.execute_callback is not None:
            return self.execute_callback(request)
        return ExecutionResult("HANDOFF_REQUIRED", self.descriptor, escalation_reason="MANAGED_CODEX_WORKER")
