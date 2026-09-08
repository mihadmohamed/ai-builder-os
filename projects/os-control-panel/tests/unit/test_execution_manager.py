from __future__ import annotations

from dataclasses import dataclass
import unittest

from execution import Availability, CodexExecutor, DeterministicWorker, ExecutionManager, ExecutionPolicy, ExecutionRequest, ExecutionResult, ExecutorDescriptor, ExecutorTier, LocalModelExecutor, RiskLevel, TaskType


@dataclass
class FakeExecutor:
    descriptor: ExecutorDescriptor
    available: bool = True
    result: str = "SUCCESS"

    def availability(self, request):
        return Availability(self.available, "now")

    def execute(self, request):
        return ExecutionResult(self.result, self.descriptor, validation_passed=self.result == "SUCCESS", escalation_reason="SCHEMA_INVALID" if self.result != "SUCCESS" else "")


def request(**overrides):
    values = dict(project_id="p", requirement_id="R120", task_id="397", task_type=TaskType.TRANSFORM, risk=RiskLevel.LOW)
    values.update(overrides)
    return ExecutionRequest(**values)


class ExecutionManagerTests(unittest.TestCase):
    def test_local_is_shadowed_until_policy_enables_automatic_routing(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LOCAL, "qwen"))], ExecutionPolicy(local_eligible_types=frozenset({TaskType.TRANSFORM})))
        self.assertEqual(manager.route(request()).status, "SHADOW")

    def test_high_risk_never_routes_to_local_executor(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LOCAL, "qwen")), FakeExecutor(ExecutorDescriptor(ExecutorTier.LUNA, "luna"))], ExecutionPolicy(automatic_routing=True, local_eligible_types=frozenset({TaskType.TRANSFORM})))
        self.assertIs(manager.route(request(risk=RiskLevel.HIGH)).executor.tier, ExecutorTier.LUNA)

    def test_context_over_local_limit_escalates_to_codex(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LOCAL, "qwen")), FakeExecutor(ExecutorDescriptor(ExecutorTier.LUNA, "luna"))], ExecutionPolicy(automatic_routing=True, local_eligible_types=frozenset({TaskType.TRANSFORM})))
        self.assertIs(manager.route(request(context_bytes=16385)).executor.tier, ExecutorTier.LUNA)

    def test_unavailable_eligible_executor_is_waiting_not_failed(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LUNA, "luna"), available=False)], ExecutionPolicy(automatic_routing=True))
        self.assertEqual(manager.route(request(risk=RiskLevel.HIGH)).status, "WAITING_FOR_EXECUTOR")

    def test_tools_not_on_allowlist_are_fail_closed(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LUNA, "luna"))], ExecutionPolicy(automatic_routing=True))
        self.assertEqual(manager.route(request(risk=RiskLevel.HIGH, tools_requested=frozenset({"shell"}))).safe_error, "POLICY_BLOCKED")

    def test_codex_executor_is_a_handoff_not_a_second_worker(self):
        result = CodexExecutor(ExecutorTier.SOL).execute(request(risk=RiskLevel.HIGH))
        self.assertEqual(result.status, "HANDOFF_REQUIRED")
        self.assertEqual(result.executor.reasoning, "medium")

    def test_codex_executor_only_delegates_to_a_controller_supplied_callback(self):
        executor = CodexExecutor(
            ExecutorTier.TERRA,
            execute_callback=lambda value: ExecutionResult("SUCCESS", ExecutorDescriptor(ExecutorTier.TERRA, "codex:terra"), validation_passed=value.requirement_id == "R120"),
        )
        result = executor.execute(request(risk=RiskLevel.HIGH))
        self.assertEqual(result.status, "SUCCESS")
        self.assertTrue(result.validation_passed)

    def test_local_is_shadow_only_even_if_automatic_routing_is_misconfigured(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LOCAL, "qwen"))], ExecutionPolicy(automatic_routing=True, local_eligible_types=frozenset({TaskType.TRANSFORM})))
        result = manager.route(request(context="Authorization: Bearer private-token"))
        self.assertEqual(result.status, "SHADOW")
        self.assertEqual(result.output, {"context_bytes": 25, "redactions": 1})
        self.assertEqual(manager.store.attempts[-1].status, "SHADOW")

    def test_context_bound_and_tool_work_cannot_select_local(self):
        manager = ExecutionManager([FakeExecutor(ExecutorDescriptor(ExecutorTier.LOCAL, "qwen")), FakeExecutor(ExecutorDescriptor(ExecutorTier.LUNA, "luna"))], ExecutionPolicy(automatic_routing=True, local_eligible_types=frozenset({TaskType.TRANSFORM}), allowed_tools=frozenset({"search"})))
        self.assertEqual(manager.route(request(context="x" * 16385)).executor.tier, ExecutorTier.LUNA)
        self.assertEqual(manager.route(request(tools_requested=frozenset({"search"}))).executor.tier, ExecutorTier.LUNA)

    def test_deterministic_worker_requires_an_explicit_allow_list(self):
        worker = DeterministicWorker({"safe": lambda: "ok", "other": lambda: "no"}, frozenset({"safe"}))
        self.assertTrue(worker.availability(request(task_id="safe")).available)
        self.assertFalse(worker.availability(request(task_id="other")).available)
        self.assertEqual(worker.execute(request(task_id="other")).safe_error, "UNSUPPORTED_DETERMINISTIC_TASK")

    def test_local_adapter_rejects_non_loopback_or_non_ollama_endpoints(self):
        with self.assertRaises(ValueError):
            LocalModelExecutor(endpoint="http://127.0.0.1:11434.evil")
        with self.assertRaises(ValueError):
            LocalModelExecutor(endpoint="http://localhost:11434")
