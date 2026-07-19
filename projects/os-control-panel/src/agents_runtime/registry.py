from __future__ import annotations

from typing import Any

from agents import Agent, ModelSettings
from agents.models.interface import Model

from pm_contract import PMDecisionEnvelope

from .guardrails import ai_builder_os_input_guardrail, ai_builder_os_output_guardrail
from .schemas import WorkflowReviewOutput
from .support import canonical_role_prompt
from .tools import (
    RuntimeContext,
    apply_pm_proposal,
    get_deterministic_next_action,
    inspect_product_history,
    inspect_project,
    submit_pm_decision,
    tools_for_role,
)


DEFAULT_MODEL = "gpt-5-mini"
ROLE_SLUGS = {
    "Orchestrator": "orchestrator",
    "PM": "pm",
    "Experience Designer": "experience_designer",
    "UI Designer": "ui_designer",
    "Architect": "architect",
    "Engineer": "engineer",
    "QA": "qa",
    "Learning Agent": "learning_agent",
    "Workflow Reviewer": "workflow_reviewer",
}


def _agent(
    *,
    name: str,
    instructions: str,
    model: str | Model,
    tools: list[Any] | None = None,
    handoffs: list[Agent[RuntimeContext]] | None = None,
    output_type: type[Any] | None = None,
    handoff_description: str | None = None,
) -> Agent[RuntimeContext]:
    return Agent[RuntimeContext](
        name=name,
        handoff_description=handoff_description,
        instructions=canonical_role_prompt(name, instructions),
        tools=tools or tools_for_role(name),
        handoffs=handoffs or [],
        output_type=output_type,
        input_guardrails=[ai_builder_os_input_guardrail],
        output_guardrails=[ai_builder_os_output_guardrail],
        model=model,
        model_settings=ModelSettings(),
    )


def build_agent_registry(model: str | Model = DEFAULT_MODEL) -> dict[str, Agent[RuntimeContext]]:
    """Construct the complete SDK team with delegated and manager-style orchestration."""
    architect = _agent(
        name="Architect",
        handoff_description="Reviews system boundaries, security, data flow, and implementation shape.",
        instructions="Give grounded architecture decisions, risks, and enforceable guardrails.",
        model=model,
    )
    qa = _agent(
        name="QA",
        handoff_description="Defines verification evidence and assesses release confidence.",
        instructions="Separate observed evidence from recommended tests and never invent passing results.",
        model=model,
    )
    experience = _agent(
        name="Experience Designer",
        handoff_description="Investigates user workflow friction and produces evidence-based experience findings.",
        instructions="Prioritize user problems, comprehension, and workflow quality over aesthetics.",
        model=model,
    )
    ui = _agent(
        name="UI Designer",
        handoff_description="Creates and reviews concrete interface direction and interaction guidance.",
        instructions="Provide implementable visual and interaction guidance grounded in the selected runtime.",
        model=model,
    )
    learning = _agent(
        name="Learning Agent",
        handoff_description="Teaches AI Builder OS concepts from first principles using repository evidence.",
        instructions="Teach for understanding, distinguish nearby concepts, and ground explanations in canonical artifacts.",
        model=model,
    )
    engineer = _agent(
        name="Engineer",
        handoff_description="Turns approved requirements into bounded implementation work and verification evidence.",
        instructions=(
            "Follow the deterministic controller. In an advisory SDK run, produce a bounded implementation packet; "
            "repository edits are executed through the Codex implementation lease path."
        ),
        tools=tools_for_role("Engineer")
        + [
            architect.as_tool("architect_review", "Ask Architect for a focused design and risk review."),
            qa.as_tool("qa_plan", "Ask QA for focused verification guidance."),
        ],
        model=model,
    )
    pm = _agent(
        name="PM",
        handoff_description="Clarifies product intent and turns it into actionable product artifacts.",
        instructions=(
            "Follow the canonical proposal-only PM contract. Return PMDecisionEnvelope decisions. Submit every typed decision, "
            "including NEEDS_INPUT, with submit_pm_decision. When the input contains a typed PM work request, echo it unchanged "
            "in work_request. For READY_FOR_APPROVAL, call apply_pm_proposal for the exact submitted ID and revision; application "
            "pauses for explicit human approval. Specialist consultations are advisory and must be included in the decision."
        ),
        tools=tools_for_role("PM")
        + [
            submit_pm_decision,
            apply_pm_proposal,
            architect.as_tool("architecture_consult", "Consult Architect on feasibility and risk."),
            engineer.as_tool("engineering_consult", "Consult Engineer on effort, delivery shape, and implementation uncertainty."),
            qa.as_tool("qa_consult", "Consult QA on acceptance evidence, validation design, and release risk."),
            experience.as_tool("experience_consult", "Consult Experience Designer on workflow and usability risk."),
            ui.as_tool("ui_consult", "Consult UI Designer on interface implications."),
        ],
        output_type=PMDecisionEnvelope,
        model=model,
    )
    orchestrator = _agent(
        name="Orchestrator",
        instructions=(
            "The deterministic controller owns workflow state. Call get_deterministic_next_action first. Use handoffs "
            "when a specialist should own the remaining conversation; use specialist tools for bounded consultations."
        ),
        tools=[inspect_project, get_deterministic_next_action, inspect_product_history]
        + [
            architect.as_tool("architect_review", "Run a bounded architectural consultation."),
            qa.as_tool("qa_review", "Run a bounded QA consultation."),
            experience.as_tool("experience_review", "Run a bounded experience consultation."),
            ui.as_tool("ui_review", "Run a bounded interface consultation."),
            learning.as_tool("learning_explanation", "Ask Learning Agent to explain a relevant system concept."),
        ],
        handoffs=[pm, experience, ui, engineer],
        model=model,
    )
    workflow_reviewer = _agent(
        name="Workflow Reviewer",
        instructions=(
            "Call get_deterministic_next_action and return a bounded second opinion. You cannot mutate or overrule the "
            "deterministic workflow controller."
        ),
        tools=tools_for_role("Orchestrator"),
        output_type=WorkflowReviewOutput,
        model=model,
    )
    return {
        "orchestrator": orchestrator,
        "pm": pm,
        "experience_designer": experience,
        "ui_designer": ui,
        "architect": architect,
        "engineer": engineer,
        "qa": qa,
        "learning_agent": learning,
        "workflow_reviewer": workflow_reviewer,
    }


def build_structured_role_agent(
    role: str,
    *,
    instructions: str,
    output_type: type[Any],
    model: str | Model = DEFAULT_MODEL,
) -> Agent[RuntimeContext]:
    """Clone a registered specialist contract for one structured production turn."""
    registry = build_agent_registry(model)
    slug = ROLE_SLUGS.get(role)
    if slug is None or slug not in registry:
        raise ValueError(f"Unknown SDK role: {role}")
    base = registry[slug]
    return base.clone(
        instructions=canonical_role_prompt(role, instructions),
        output_type=output_type,
        handoffs=[],
    )
