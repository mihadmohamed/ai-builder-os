from __future__ import annotations

from dataclasses import asdict
from typing import Any, Literal

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field

from control_plane import (
    EXTERNAL_APPROVAL_RISKS,
    WorkflowController,
    build_action_descriptor,
)


mcp = FastMCP(
    "ai-builder-os",
    instructions=(
        "Use this server to run the deterministic AI Builder OS control plane from Codex. Codex-native execution is "
        "the default and does not call the OpenAI API. Agents SDK tools are an explicit API-billed optional backend. "
        "Never expose lease tokens outside the active implementation turn."
    ),
)

READ_ONLY_TOOL = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)
COORDINATION_TOOL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=False,
)
CANONICAL_DECISION_TOOL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=True,
    openWorldHint=False,
)
EXTERNAL_DECISION_TOOL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=True,
    idempotentHint=False,
    openWorldHint=True,
)


class NativeApprovalForm(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: str = Field(
        pattern="^(approve|reject)$",
        json_schema_extra={"enum": ["approve", "reject"]},
        description="Approve or reject the exact action displayed by Codex.",
    )
    rejection_reason: str = Field(
        default="",
        max_length=1_000,
        description="Optional reason when rejecting.",
    )


def _elicitation_action(result: object) -> str:
    action = getattr(result, "action", "")
    return str(getattr(action, "value", action)).lower()


def _native_form_message(descriptor: dict[str, Any]) -> str:
    source_state = descriptor.get("source_state", {})
    source_lines = "\n".join(
        f"- {name}: {str(value)[:16]}"
        for name, value in sorted(source_state.items())
    )
    source_section = f"Source state:\n{source_lines}\n" if source_lines else ""
    return (
        f"AI Builder OS approval · {descriptor['risk']}\n\n"
        f"Project: {descriptor['project_name']}\n"
        f"Action: {descriptor['action_name']}\n"
        f"Target: {descriptor['target_type']} {descriptor['target_id']}"
        f" rev {descriptor['target_revision']}\n"
        f"Summary: {descriptor['summary']}\n"
        f"Human authority: {descriptor['actor_boundary']}\n"
        f"Idempotency: {descriptor['idempotency_identity']}\n"
        f"{source_section}"
        f"Seal: {descriptor['sealed_payload_sha256'][:16]}\n\n"
        "Choose Approve only if this exact action and revision are authorized. "
        "Cancel the Codex prompt to leave it pending."
    )


def _agents_sdk_runtime():
    from agents_runtime import AgentsWorkflowRuntime

    return AgentsWorkflowRuntime()


@mcp.tool(annotations=READ_ONLY_TOOL)
def list_projects() -> list[str]:
    """List projects governed by AI Builder OS product files."""
    return WorkflowController().list_projects()


@mcp.tool(annotations=READ_ONLY_TOOL)
def inspect_project(project_name: str) -> dict[str, Any]:
    """Read canonical requirements, tasks, approvals, runs, and content hashes."""
    return WorkflowController().snapshot(project_name)


@mcp.tool(annotations=READ_ONLY_TOOL)
def get_next_action(project_name: str) -> dict[str, Any]:
    """Return the deterministic controller's next action and role."""
    return WorkflowController().next_action(project_name).to_dict()


@mcp.tool(annotations=READ_ONLY_TOOL)
def get_execution_backends() -> dict[str, dict[str, Any]]:
    """Describe the default Codex-native backend and the optional API-billed Agents SDK backend."""
    return {
        "codex_native": {
            "default": True,
            "billing": "Codex plan/credits",
            "model_runtime": "current Codex chat and optional Codex subagents",
            "controller": "local deterministic MCP tools",
            "token_reporting": "Codex usage is managed by Codex; the controller does not invent token counts",
        },
        "deterministic_controller": {
            "default": True,
            "billing": "No model tokens",
            "model_runtime": "none",
            "operations": "queues, PM proposals, approvals, validation, canonical application, and history",
        },
        "agents_sdk": {
            "default": False,
            "billing": "OpenAI API project",
            "model_runtime": "OpenAI Agents SDK",
            "requires_explicit_user_request": True,
            "token_reporting": "model requests and provider-reported input/output tokens are recorded",
            "dual_usage_warning": "Calling this backend from Codex uses Codex for the surrounding chat and API tokens for the SDK run",
        },
    }


@mcp.tool(annotations=READ_ONLY_TOOL)
def get_approval_risk_policy() -> dict[str, Any]:
    """Return the deterministic action-to-risk policy without invoking a model."""
    return WorkflowController().approval_risk_policy()


@mcp.tool(annotations=COORDINATION_TOOL)
def record_product_intent(
    project_name: str,
    intent: str,
    actor: str = "codex-chat",
    idempotency_key: str = "",
) -> dict[str, Any]:
    """Record durable product intent, not a raw chat transcript or private reasoning."""
    return WorkflowController().record_intent(
        project_name,
        intent,
        actor=actor,
        source="codex-mcp",
        idempotency_key=idempotency_key,
    )


@mcp.tool(annotations=READ_ONLY_TOOL)
def list_pm_proposals(
    project_name: str,
    status: str = "PENDING_APPROVAL",
) -> list[dict[str, Any]]:
    """List durable PM proposals without invoking a model."""
    statuses = (status.strip().upper(),) if status.strip() else ()
    return WorkflowController().list_pm_proposals(project_name, statuses=statuses)


@mcp.tool(annotations=COORDINATION_TOOL)
def submit_pm_proposal(
    project_name: str,
    proposal: dict[str, Any],
    actor: str = "codex-chat",
    idempotency_key: str = "",
    origin_request_id: str = "",
) -> dict[str, Any]:
    """Submit a typed, read-only PM decision for conversational approval; this is model-free."""
    return WorkflowController().submit_pm_proposal(
        project_name,
        proposal,
        actor=actor,
        source="codex-mcp",
        idempotency_key=idempotency_key,
        origin_request_id=origin_request_id,
    )


@mcp.tool(annotations=READ_ONLY_TOOL)
def describe_pm_proposal_action(
    project_name: str,
    proposal_id: str,
    proposal_revision: int,
    decision: Literal["approve", "reject"] = "approve",
) -> dict[str, Any]:
    """Return the sealed exact-action descriptor that a human approval would authorize."""
    return WorkflowController().describe_pm_proposal_action(
        project_name,
        proposal_id,
        proposal_revision,
        decision=decision,
    )


@mcp.tool(annotations=CANONICAL_DECISION_TOOL)
async def decide_pm_proposal(
    context: Context,
    project_name: str,
    proposal_id: str,
    proposal_revision: int,
) -> dict[str, Any]:
    """Elicit a native human decision for one exact PM proposal revision.

    No canonical state changes before the client returns an accepted Approve or
    Reject form response. Decline, cancel, unsupported clients, and failures
    leave the proposal pending for chat or Streamlit review.
    """
    controller = WorkflowController()
    decision_descriptor = controller.describe_pm_proposal_decision(
        project_name,
        proposal_id,
        proposal_revision,
    )
    try:
        result = await context.elicit(
            message=_native_form_message(decision_descriptor),
            schema=NativeApprovalForm,
        )
    except Exception as exc:
        return {
            "status": "FALLBACK_REQUIRED",
            "proposal_id": proposal_id,
            "proposal_revision": proposal_revision,
            "detail": (
                "Native Codex elicitation was unavailable. Use explicit chat confirmation "
                f"or the Streamlit Workflow Inbox. Error type: {type(exc).__name__}."
            ),
        }
    action = _elicitation_action(result)
    if action != "accept":
        return {
            "status": "PENDING_APPROVAL",
            "proposal_id": proposal_id,
            "proposal_revision": proposal_revision,
            "detail": f"Native approval was {action or 'cancelled'}; no product state changed.",
        }
    try:
        form = NativeApprovalForm.model_validate(getattr(result, "data", None))
    except Exception:
        return {
            "status": "PENDING_APPROVAL",
            "proposal_id": proposal_id,
            "proposal_revision": proposal_revision,
            "detail": "Native approval response was malformed; no product state changed.",
        }
    decision = str(form.decision)
    try:
        record = controller.decide_pm_proposal_from_native_prompt(
            project_name,
            proposal_id,
            proposal_revision,
            decision=decision,
            expected_seal=decision_descriptor["sealed_payload_sha256"],
            actor="product-director-via-codex",
            rejection_reason=str(form.rejection_reason),
        )
    except ValueError as exc:
        return {
            "status": "STALE_OR_INVALID",
            "proposal_id": proposal_id,
            "proposal_revision": proposal_revision,
            "detail": f"No product state changed. {exc}",
        }
    return {
        "status": record["status"],
        "proposal_id": record["proposal_id"],
        "proposal_revision": record["proposal_revision"],
        "decision_source": "codex-native-elicitation",
        "sealed_payload_sha256": decision_descriptor["sealed_payload_sha256"],
    }


@mcp.tool(annotations=CANONICAL_DECISION_TOOL)
def approve_pm_proposal(
    project_name: str,
    proposal_id: str,
    proposal_revision: int,
    actor: str = "codex-chat",
) -> dict[str, Any]:
    """Apply the exact PM proposal revision after the user has approved it in this chat."""
    return WorkflowController().approve_pm_proposal(
        project_name,
        proposal_id,
        proposal_revision,
        actor=actor,
        source="codex-mcp",
    )


@mcp.tool(annotations=CANONICAL_DECISION_TOOL)
def reject_pm_proposal(
    project_name: str,
    proposal_id: str,
    proposal_revision: int,
    reason: str = "",
    actor: str = "codex-chat",
) -> dict[str, Any]:
    """Reject the exact PM proposal revision and preserve the conversational decision."""
    return WorkflowController().reject_pm_proposal(
        project_name,
        proposal_id,
        proposal_revision,
        actor=actor,
        source="codex-mcp",
        reason=reason,
    )


@mcp.tool(annotations=COORDINATION_TOOL)
def create_codex_work_request(
    project_name: str,
    task: str,
    requirement_id: str = "",
    requested_role: str = "engineer",
    actor: str = "codex-chat",
    idempotency_key: str = "",
) -> dict[str, Any]:
    """Create a durable READY_FOR_CODEX request without invoking any API-backed agent runtime."""
    return WorkflowController().create_codex_work_request(
        project_name,
        task,
        requested_by=actor,
        source="codex-mcp",
        requested_role=requested_role,
        requirement_id=requirement_id,
        idempotency_key=idempotency_key,
    ).to_dict()


@mcp.tool(annotations=COORDINATION_TOOL)
def create_pm_codex_work_request(
    project_name: str,
    mode: str,
    target_requirement_ids: list[str],
    operator_context: str = "",
    parent_proposal_id: str = "",
    parent_proposal_revision: int = 0,
    actor: str = "codex-chat",
    idempotency_key: str = "",
) -> dict[str, Any]:
    """Create a typed PM prioritisation or task-planning request for Codex without invoking a model."""
    return WorkflowController().create_pm_codex_work_request(
        project_name,
        {
            "mode": mode,
            "target_requirement_ids": target_requirement_ids,
            "operator_context": operator_context,
            "parent_proposal_id": parent_proposal_id,
            "parent_proposal_revision": parent_proposal_revision,
        },
        requested_by=actor,
        source="codex-mcp",
        idempotency_key=idempotency_key,
    ).to_dict()


@mcp.tool(annotations=READ_ONLY_TOOL)
def list_codex_work_requests(
    project_name: str,
    status: str = "READY_FOR_CODEX",
) -> list[dict[str, Any]]:
    """List Codex-native work requests; pass an empty status to include every state."""
    statuses = (status,) if status.strip() else ()
    return [item.to_dict() for item in WorkflowController().list_codex_work_requests(project_name, statuses=statuses)]


@mcp.tool(annotations=COORDINATION_TOOL)
def claim_codex_work_request(
    project_name: str,
    request_id: str,
    actor: str = "codex-chat",
    lease_minutes: int = 240,
) -> dict[str, Any]:
    """Claim one READY_FOR_CODEX request with a bounded, reclaimable coordination lease."""
    return WorkflowController().claim_codex_work_request(
        project_name,
        request_id,
        actor=actor,
        lease_minutes=lease_minutes,
    ).to_dict()


@mcp.tool(annotations=COORDINATION_TOOL)
def resolve_codex_work_request(
    project_name: str,
    request_id: str,
    status: str,
    summary: str,
    implementation_run_id: str = "",
    result_proposal_id: str = "",
    result_proposal_revision: int = 0,
    actor: str = "codex-chat",
) -> dict[str, Any]:
    """Close a Codex-native request and append its outcome to canonical product history."""
    return WorkflowController().resolve_codex_work_request(
        project_name,
        request_id,
        actor=actor,
        status=status,
        summary=summary,
        implementation_run_id=implementation_run_id,
        result_proposal_id=result_proposal_id,
        result_proposal_revision=result_proposal_revision,
    ).to_dict()


@mcp.tool(annotations=COORDINATION_TOOL)
def claim_implementation(
    project_name: str,
    requirement_id: str,
    actor: str = "codex-chat",
    idempotency_key: str = "",
) -> dict[str, Any]:
    """Acquire an exclusive bounded lease and return the work packet for this Codex chat."""
    return WorkflowController().claim_implementation(
        project_name,
        requirement_id,
        executor=actor,
        idempotency_key=idempotency_key,
    ).to_dict()


@mcp.tool(annotations=COORDINATION_TOOL)
def record_implementation_evidence(
    project_name: str,
    run_id: str,
    lease_token: str,
    summary: str,
    files_changed: list[str],
    tests: list[str],
    status: str = "COMPLETED",
) -> dict[str, Any]:
    """Close a claimed implementation with file and test evidence in canonical history."""
    return WorkflowController().record_implementation_evidence(
        project_name,
        run_id,
        lease_token,
        summary=summary,
        files_changed=files_changed,
        tests=tests,
        status=status,
    )


@mcp.tool(annotations=READ_ONLY_TOOL)
def read_product_history(project_name: str, limit: int = 50) -> list[dict[str, Any]]:
    """Read recent canonical workflow history events."""
    return WorkflowController().history(project_name, limit=min(200, max(1, limit)))


@mcp.tool(annotations=READ_ONLY_TOOL)
def list_agent_approvals(project_name: str) -> list[dict[str, Any]]:
    """List optional API-backed SDK approvals without exposing serialized state or secrets."""
    return WorkflowController().snapshot(project_name)["sdk_approvals"]


@mcp.tool(annotations=READ_ONLY_TOOL)
def list_external_approvals(project_name: str) -> list[dict[str, Any]]:
    """List open external/public action approvals without exposing private runtime state."""
    from workspace import list_approvals

    return [
        {
            "approval_id": item.approval_id,
            "approval_type": item.approval_type,
            "project_name": item.project_name,
            "title": item.title,
            "summary": item.summary,
            "created_at": item.created_at,
        }
        for item in list_approvals(project_name)
        if item.status == "OPEN" and item.approval_type in EXTERNAL_APPROVAL_RISKS
    ]


@mcp.tool(annotations=EXTERNAL_DECISION_TOOL)
async def decide_external_approval(
    context: Context,
    project_name: str,
    approval_id: str,
) -> dict[str, Any]:
    """Elicit a separate native human decision for an exact external action."""
    from workspace import approve_request, list_approvals, reject_request

    approval = next(
        (
            item
            for item in list_approvals(project_name)
            if item.approval_id == approval_id and item.status == "OPEN"
        ),
        None,
    )
    if approval is None:
        raise ValueError(f"Open external approval not found: {approval_id}")
    if approval.approval_type not in EXTERNAL_APPROVAL_RISKS:
        raise ValueError(f"Approval is not an external-action approval: {approval.approval_type}")
    descriptor = build_action_descriptor(
        project_name=project_name,
        action_name="decide_external_approval",
        target_type=approval.approval_type,
        target_id=approval.approval_id,
        target_revision=0,
        summary=f"{approval.title}: {approval.summary}",
        source_state={},
        actor_boundary="product-director-human",
        idempotency_identity=f"external-approval:{project_name}:{approval.approval_id}",
        sealed_payload=asdict(approval),
    ).model_dump(mode="json")
    try:
        result = await context.elicit(
            message=_native_form_message(descriptor),
            schema=NativeApprovalForm,
        )
    except Exception as exc:
        return {
            "status": "FALLBACK_REQUIRED",
            "approval_id": approval_id,
            "detail": (
                "Native Codex elicitation was unavailable. Use the Streamlit Workflow Inbox. "
                f"Error type: {type(exc).__name__}."
            ),
        }
    action = _elicitation_action(result)
    if action != "accept":
        return {
            "status": "OPEN",
            "approval_id": approval_id,
            "detail": f"Native approval was {action or 'cancelled'}; no external action ran.",
        }
    try:
        form = NativeApprovalForm.model_validate(getattr(result, "data", None))
    except Exception:
        return {
            "status": "OPEN",
            "approval_id": approval_id,
            "detail": "Native approval response was malformed; no external action ran.",
        }
    current = next(
        (
            item
            for item in list_approvals(project_name)
            if item.approval_id == approval_id and item.status == "OPEN"
        ),
        None,
    )
    if current is None or asdict(current) != asdict(approval):
        return {
            "status": "OPEN",
            "approval_id": approval_id,
            "detail": "External approval changed after display; refresh and approve the new exact action.",
        }
    resolved = (
        approve_request(project_name, approval_id)
        if form.decision == "approve"
        else reject_request(project_name, approval_id)
    )
    controller = WorkflowController()
    controller.record_native_external_approval_decision(
        project_name,
        approval_id=approval_id,
        approval_type=approval.approval_type,
        decision=str(form.decision),
        sealed_payload_sha256=descriptor["sealed_payload_sha256"],
        actor="product-director-via-codex",
    )
    return {
        "status": resolved.status,
        "approval_id": approval_id,
        "decision_source": "codex-native-elicitation",
        "sealed_payload_sha256": descriptor["sealed_payload_sha256"],
    }


@mcp.tool(annotations=EXTERNAL_DECISION_TOOL)
async def start_agent_workflow(
    context: Context,
    project_name: str,
    prompt: str,
    agent_name: str = "orchestrator",
    actor: str = "codex-chat",
    session_id: str = "",
) -> dict[str, Any]:
    """Elicit explicit human permission before starting an API-billed Agents SDK run."""
    descriptor = build_action_descriptor(
        project_name=project_name,
        action_name="start_agent_workflow",
        target_type="agents_sdk_run",
        target_id=session_id.strip() or "new-session",
        target_revision=0,
        summary=f"Start API-billed Agents SDK agent '{agent_name}' for {project_name}.",
        source_state={},
        actor_boundary="api-billing-authority-human",
        idempotency_identity=f"agents-sdk-start:{project_name}:{session_id.strip() or 'new'}",
        sealed_payload={
            "project_name": project_name,
            "prompt": prompt,
            "agent_name": agent_name,
            "actor": "product-director-via-codex",
            "session_id": session_id,
        },
    ).model_dump(mode="json")
    try:
        result = await context.elicit(
            message=_native_form_message(descriptor),
            schema=NativeApprovalForm,
        )
    except Exception as exc:
        return {
            "status": "FALLBACK_REQUIRED",
            "detail": (
                "Native Codex elicitation was unavailable. No API request was made. "
                f"Error type: {type(exc).__name__}."
            ),
        }
    action = _elicitation_action(result)
    if action != "accept":
        return {
            "status": "NOT_STARTED",
            "detail": "API-billed workflow was not approved; no API request was made.",
        }
    try:
        form = NativeApprovalForm.model_validate(getattr(result, "data", None))
    except Exception:
        return {
            "status": "NOT_STARTED",
            "detail": "Native approval response was malformed; no API request was made.",
        }
    if form.decision != "approve":
        return {
            "status": "NOT_STARTED",
            "detail": "API-billed workflow was rejected; no API request was made.",
        }
    return _agents_sdk_runtime().run(
        project_name,
        prompt,
        agent_name=agent_name,
        actor="product-director-via-codex",
        source="codex-native-elicitation",
        session_id=session_id,
    )


@mcp.tool(annotations=EXTERNAL_DECISION_TOOL)
async def resolve_agent_approval(
    context: Context,
    project_name: str,
    run_id: str,
    approval_id: str,
    approve: bool,
    actor: str = "codex-chat",
    rejection_message: str = "",
) -> dict[str, Any]:
    """Elicit a separate human decision before resuming one exact API-backed approval."""
    decision = "approve" if approve else "reject"
    descriptor = build_action_descriptor(
        project_name=project_name,
        action_name="resolve_agent_approval",
        target_type="agents_sdk_approval",
        target_id=approval_id,
        target_revision=0,
        summary=f"{decision.title()} SDK approval {approval_id} in run {run_id}.",
        source_state={"run_id": run_id},
        actor_boundary="api-and-side-effect-authority-human",
        idempotency_identity=f"agents-sdk-resume:{project_name}:{run_id}:{approval_id}:{decision}",
        sealed_payload={
            "project_name": project_name,
            "run_id": run_id,
            "approval_id": approval_id,
            "approve": approve,
            "actor": "product-director-via-codex",
            "rejection_message": rejection_message,
        },
    ).model_dump(mode="json")
    try:
        result = await context.elicit(
            message=_native_form_message(descriptor),
            schema=NativeApprovalForm,
        )
    except Exception as exc:
        return {
            "status": "FALLBACK_REQUIRED",
            "detail": (
                "Native Codex elicitation was unavailable. The SDK run remains paused. "
                f"Error type: {type(exc).__name__}."
            ),
        }
    action = _elicitation_action(result)
    if action != "accept":
        return {
            "status": "AWAITING_APPROVAL",
            "detail": "SDK approval resolution was not authorized; the run remains paused.",
        }
    try:
        form = NativeApprovalForm.model_validate(getattr(result, "data", None))
    except Exception:
        return {
            "status": "AWAITING_APPROVAL",
            "detail": "Native approval response was malformed; the SDK run remains paused.",
        }
    if form.decision != "approve":
        return {
            "status": "AWAITING_APPROVAL",
            "detail": "SDK approval resolution was rejected; the run remains paused.",
        }
    return _agents_sdk_runtime().resume(
        project_name,
        run_id,
        approval_id,
        approve=approve,
        actor="product-director-via-codex",
        rejection_message=rejection_message,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
