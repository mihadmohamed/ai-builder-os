from __future__ import annotations

from typing import Any

from agents import Agent, RunContextWrapper, RunHooks, Tool

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
        self._record(
            context,
            "tool_completed",
            agent=agent.name,
            tool=getattr(tool, "name", type(tool).__name__),
            output_chars=len(str(result)),
        )

    async def on_llm_start(self, context, agent: Agent[RuntimeContext], system_prompt, input_items) -> None:
        self._record(context, "model_call", agent=agent.name)

    async def on_llm_end(self, context, agent: Agent[RuntimeContext], response) -> None:
        usage = getattr(response, "usage", None)
        self._record(
            context,
            "model_response",
            agent=agent.name,
            input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
            output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        )
