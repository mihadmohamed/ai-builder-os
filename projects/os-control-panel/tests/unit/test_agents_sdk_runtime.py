from __future__ import annotations

from contextlib import nullcontext
import json
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents import ModelResponse, Usage
from agents.models.interface import Model
from openai.types.responses import ResponseFunctionToolCall, ResponseOutputMessage, ResponseOutputText

from agents_runtime.registry import build_agent_registry
from agents_runtime.runner import AgentsWorkflowRuntime, DISABLE_TRACING_ENV
from agents_runtime.schemas import WorkflowReviewOutput
from agents_runtime.tools import _validate_public_url, tools_for_role
from control_plane import WorkflowController
import workspace


class _ApprovalModel(Model):
    """Scripted SDK model: request an approved write, then finish."""

    def __init__(self) -> None:
        self.requests = 0

    async def get_response(self, *args, **kwargs) -> ModelResponse:
        self.requests += 1
        if self.requests == 1:
            output = [
                ResponseFunctionToolCall(
                    arguments=json.dumps({"intent": "Keep one canonical product history."}),
                    call_id="approval-call-1",
                    name="record_product_intent",
                    type="function_call",
                )
            ]
        else:
            output = [
                ResponseOutputMessage(
                    id="approval-complete-1",
                    content=[ResponseOutputText(annotations=[], text="Intent recorded.", type="output_text")],
                    role="assistant",
                    status="completed",
                    type="message",
                )
            ]
        return ModelResponse(
            output=output,
            usage=Usage(requests=1, input_tokens=3, output_tokens=2, total_tokens=5),
            response_id=f"scripted-{self.requests}",
        )

    async def stream_response(self, *args, **kwargs):
        if False:
            yield None


class AgentsSDKRuntimeTests(unittest.TestCase):
    def test_registry_has_real_handoffs_agents_as_tools_and_approval(self) -> None:
        registry = build_agent_registry()

        self.assertEqual(
            {agent.name for agent in registry["orchestrator"].handoffs},
            {"PM", "Experience Designer", "UI Designer", "Engineer"},
        )
        self.assertTrue(any(getattr(tool, "_is_agent_tool", False) for tool in registry["orchestrator"].tools))
        intent_tool = next(tool for tool in registry["pm"].tools if tool.name == "record_product_intent")
        self.assertTrue(intent_tool.needs_approval)
        self.assertIs(registry["workflow_reviewer"].output_type, WorkflowReviewOutput)
        self.assertEqual(len(registry), 9)
        for agent in registry.values():
            self.assertTrue(agent.input_guardrails, agent.name)
            self.assertTrue(agent.output_guardrails, agent.name)

    def test_roles_have_explicit_least_privilege_tools_and_ssrf_boundary(self) -> None:
        self.assertIn("get_deterministic_next_action", {tool.name for tool in tools_for_role("Engineer")})
        self.assertNotIn("record_product_intent", {tool.name for tool in tools_for_role("Engineer")})
        with self.assertRaises(ValueError):
            _validate_public_url("http://localhost:8501/private")
        with self.assertRaises(ValueError):
            _validate_public_url("file:///etc/passwd")

    def test_legacy_custom_loop_and_tool_request_protocol_are_removed(self) -> None:
        src_root = Path(__file__).resolve().parents[2] / "src"
        self.assertFalse((src_root / "agent_runtime.py").exists())
        forbidden = ("run_structured_agent", "tool_requests", "client.responses.parse")
        offenders: list[str] = []
        for path in src_root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if any(token in text for token in forbidden):
                offenders.append(str(path.relative_to(src_root)))
        self.assertEqual(offenders, [])

    def test_real_sdk_run_serializes_approval_and_resumes_exactly_once(self) -> None:
        model = _ApprovalModel()
        runtime = AgentsWorkflowRuntime(model=model)
        recorded: list[str] = []

        def record_intent(_controller, _project_name, intent, **kwargs):
            recorded.append(intent)
            return {"event_type": "intent_recorded", "intent": intent}

        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir)
            with patch.dict(os.environ, {DISABLE_TRACING_ENV: "1"}, clear=False):
                with patch("agents_runtime.runner.control_data_dir", return_value=data_dir):
                    with patch("agents_runtime.runner.project_lock", side_effect=lambda _project: nullcontext()):
                        with patch("agents_runtime.runner.append_history"):
                            with patch("agents_runtime.runner.append_agent_trace"):
                                with patch.object(WorkflowController, "record_intent", new=record_intent):
                                    paused = runtime.run(
                                        "os-control-panel",
                                        "Record the durable product intent.",
                                        agent_name="pm",
                                    )
                                    self.assertEqual(paused["status"], "AWAITING_APPROVAL")
                                    self.assertEqual(recorded, [])
                                    self.assertTrue((data_dir / "pending_agent_runs.json").exists())

                                    completed = runtime.resume(
                                        "os-control-panel",
                                        paused["run_id"],
                                        paused["approvals"][0]["approval_id"],
                                        approve=True,
                                        actor="test-user",
                                    )

        self.assertEqual(completed["status"], "COMPLETED")
        self.assertEqual(completed["final_output"], "Intent recorded.")
        self.assertEqual(recorded, ["Keep one canonical product history."])
        self.assertEqual(model.requests, 2)

    def test_runtime_uses_sdk_runner_session_and_trace_metadata(self) -> None:
        output = WorkflowReviewOutput(
            recommended_role="Engineer",
            recommended_action="Implement R1",
            rationale="The controller selected it.",
            agrees_with_deterministic=True,
        )
        fake_result = SimpleNamespace(
            interruptions=[],
            final_output=output,
            last_agent=SimpleNamespace(name="Workflow Reviewer"),
        )
        runtime = AgentsWorkflowRuntime()
        with patch.object(runtime, "_session", return_value=SimpleNamespace(close=lambda: None)):
            with patch("agents_runtime.runner.append_history"):
                with patch("agents_runtime.runner.append_agent_trace"):
                    with patch("agents_runtime.runner.Runner.run_sync", return_value=fake_result) as run_sync:
                        result = runtime.run("os-control-panel", "Review", agent_name="workflow_reviewer")

        self.assertEqual(result["final_output"]["recommended_role"], "Engineer")
        config = run_sync.call_args.kwargs["run_config"]
        self.assertEqual(config.group_id, "os-control-panel")
        self.assertEqual(config.trace_id, result["trace_id"])
        self.assertEqual(config.workflow_name, "AI Builder OS deterministic workflow")

    def test_streamlit_workflow_review_uses_sdk_runtime_only_when_enabled(self) -> None:
        deterministic = workspace.OrchestratorRecommendation("Run Engineer on R1.", "Engineer", "R1 is ready.")
        sdk_output = workspace.LiveOrchestratorReviewTurn(
            recommended_role="Engineer",
            recommended_action="Run Engineer on R1.",
            rationale="The deterministic recommendation is supported.",
            agrees_with_deterministic=True,
            uncertainty="",
        )
        with patch.dict("os.environ", {"AI_BUILDER_OS_ENABLE_API_AGENTS": "1"}):
            with patch("workspace.orchestrator_recommendation", return_value=deterministic):
                with patch("agents_runtime.AgentsWorkflowRuntime") as runtime_class:
                    runtime_class.return_value.run_structured.return_value = sdk_output
                    review = workspace.run_live_orchestrator_review("os-control-panel")

        self.assertTrue(review.agrees_with_deterministic)
        self.assertEqual(runtime_class.return_value.run_structured.call_args.kwargs["role"], "Orchestrator")

    def test_streamlit_workflow_review_does_not_call_sdk_by_default(self) -> None:
        deterministic = workspace.OrchestratorRecommendation("Run Engineer on R1.", "Engineer", "R1 is ready.")
        with patch.dict("os.environ", {}, clear=True):
            with patch("workspace.orchestrator_recommendation", return_value=deterministic):
                with patch("agents_runtime.AgentsWorkflowRuntime") as runtime_class:
                    with self.assertRaisesRegex(workspace.LivePMDiscoveryError, "API-backed live agents are disabled"):
                        workspace.run_live_orchestrator_review("os-control-panel")

        runtime_class.assert_not_called()


if __name__ == "__main__":
    unittest.main()
