from __future__ import annotations

import json
from typing import Any

from agents import Agent, GuardrailFunctionOutput, RunContextWrapper, input_guardrail, output_guardrail

from .support import AgentRunLimits, inspect_agent_input, inspect_agent_output
from .tools import RuntimeContext


@input_guardrail(name="ai_builder_os_input_policy", run_in_parallel=False)
def ai_builder_os_input_guardrail(
    context: RunContextWrapper[RuntimeContext],
    agent: Agent[RuntimeContext],
    agent_input: str | list[dict[str, Any]],
) -> GuardrailFunctionOutput:
    """Block oversized or instruction-manipulation input before tools or models run."""
    rendered = agent_input if isinstance(agent_input, str) else json.dumps(agent_input, default=str)
    findings = inspect_agent_input(rendered, limits=AgentRunLimits())
    context.context.setdefault("guardrail_findings", []).extend(
        {"boundary": "input", "kind": item.kind, "severity": item.severity, "detail": item.detail}
        for item in findings
    )
    return GuardrailFunctionOutput(
        output_info=[item.__dict__ for item in findings],
        tripwire_triggered=any(item.severity == "blocked" for item in findings),
    )


@output_guardrail(name="ai_builder_os_output_policy")
def ai_builder_os_output_guardrail(
    context: RunContextWrapper[RuntimeContext],
    agent: Agent[RuntimeContext],
    output: Any,
) -> GuardrailFunctionOutput:
    """Block empty responses and unsupported claims of consequential actions."""
    findings = inspect_agent_output(output)
    context.context.setdefault("guardrail_findings", []).extend(
        {"boundary": "output", "kind": item.kind, "severity": item.severity, "detail": item.detail}
        for item in findings
    )
    return GuardrailFunctionOutput(
        output_info=[item.__dict__ for item in findings],
        tripwire_triggered=any(item.severity == "blocked" for item in findings),
    )
