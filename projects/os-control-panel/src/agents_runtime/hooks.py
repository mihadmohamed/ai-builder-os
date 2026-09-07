from __future__ import annotations

from typing import Any

from agents import Agent, RunContextWrapper, RunHooks, Tool

from context_attribution import ContextContribution, measured_contribution

from .support import append_agent_trace
from .tools import RuntimeContext


class OSRunHooks(RunHooks[RuntimeContext]):
    """Mirror high-value SDK lifecycle events locally with the SDK trace ID."""

    @staticmethod
    def _record(context: RunContextWrapper[RuntimeContext], event: str, **payload: Any) -> None:
        project_name = str(context.context.get("project_name", "os-control-panel"))
        append_agent_trace(
            project_name,
            {
                "trace_id": str(context.context.get("trace_id", "")),
                "run_id": str(context.context.get("run_id", "")),
                "event": event,
                "runtime": "openai_agents_sdk",
                **payload,
            },
        )

    async def on_agent_start(self, context, agent: Agent[RuntimeContext]) -> None:
        context.context["active_role"] = agent.name
        self._record(context, "agent_started", agent=agent.name)

    async def on_agent_end(self, context, agent: Agent[RuntimeContext], output: Any) -> None:
        self._record(context, "agent_completed", agent=agent.name)

    async def on_handoff(self, context, from_agent: Agent[RuntimeContext], to_agent: Agent[RuntimeContext]) -> None:
        self._record(context, "handoff", from_agent=from_agent.name, to_agent=to_agent.name)

    async def on_tool_start(self, context, agent: Agent[RuntimeContext], tool: Tool) -> None:
        self._record(context, "tool_started", agent=agent.name, tool=getattr(tool, "name", type(tool).__name__))

    async def on_tool_end(self, context, agent: Agent[RuntimeContext], tool: Tool, result: object) -> None:
        tool_name = getattr(tool, "name", type(tool).__name__)
        identity = {
            "project_name": str(context.context.get("project_name", "")),
            "run_id": str(context.context.get("run_id", "")),
            "trace_id": str(context.context.get("trace_id", "")),
            "role": agent.name,
            "tool_name": tool_name,
        }
        contribution = measured_contribution(
            "tool_results",
            str(result),
            source=f"agents_sdk_tool_return:{tool_name}",
            workflow_identity=identity,
            adapter_version="openai-agents-sdk-hooks.v1",
            source_schema_version="tool-return-string.v1",
            truncated=str(result).endswith("...[truncated]"),
        )
        self._record(
            context,
            "tool_completed",
            agent=agent.name,
            tool=tool_name,
            output_chars=len(str(result)),
            output_bytes=len(str(result).encode("utf-8")),
            context_contributions=[contribution.model_dump(mode="json")],
        )

    async def on_llm_start(self, context, agent: Agent[RuntimeContext], system_prompt, input_items) -> None:
        contributions: list[ContextContribution] = []
        for item in context.context.get("context_contributions", []):
            try:
                contributions.append(ContextContribution.model_validate(item))
            except (TypeError, ValueError):
                continue
        identity = {
            "project_name": str(context.context.get("project_name", "")),
            "run_id": str(context.context.get("run_id", "")),
            "trace_id": str(context.context.get("trace_id", "")),
            "role": agent.name,
            "workflow_mode": str(context.context.get("pm_mode") or "default"),
        }
        instruction_categories = {
            "global_instructions", "role_instructions", "mode_instructions", "runtime_instructions"
        }
        if not any(item.category in instruction_categories for item in contributions):
            contributions.append(measured_contribution(
                "global_instructions",
                str(system_prompt or ""),
                source="agents_sdk_model_system_prompt",
                workflow_identity=identity,
                adapter_version="openai-agents-sdk-hooks.v1",
                source_schema_version="model-system-prompt-string.v1",
            ))
        session = measured_contribution(
            "session_context",
            str(input_items or ""),
            source="agents_sdk_model_input_items",
            workflow_identity=identity,
            adapter_version="openai-agents-sdk-hooks.v1",
            source_schema_version="model-input-items-string.v1",
        )
        contributions = [item for item in contributions if item.category != "session_context"] + [session]
        static_size = sum(
            int(item.value or 0)
            for item in contributions
            if item.category in instruction_categories and item.unit == "characters"
        )
        project_categories = {
            "requirements_context", "tasks_context", "memory_context", "rules_context",
            "active_workflow_context", "specialist_results",
        }
        project_size = sum(
            int(item.value or 0)
            for item in contributions
            if item.category in project_categories and item.unit == "characters"
        )
        context.context["project_context_size"] = project_size if project_size else None
        self._record(
            context,
            "model_call",
            agent=agent.name,
            static_instruction_size=static_size,
            project_context_size=project_size if project_size else None,
            session_context_size=int(session.value or 0),
            context_contributions=[item.model_dump(mode="json") for item in contributions],
        )

    async def on_llm_end(self, context, agent: Agent[RuntimeContext], response) -> None:
        usage = getattr(response, "usage", None)
        input_details = getattr(usage, "input_tokens_details", None)
        output_details = getattr(usage, "output_tokens_details", None)
        self._record(
            context,
            "model_response",
            agent=agent.name,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            cached_input_tokens=int(getattr(input_details, "cached_tokens", 0) or 0),
            cache_write_tokens=int(getattr(input_details, "cache_write_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
            reasoning_tokens=int(getattr(output_details, "reasoning_tokens", 0) or 0),
            model_requests=int(getattr(usage, "requests", 0) or 0),
            model=str(getattr(response, "model", "") or ""),
        )
