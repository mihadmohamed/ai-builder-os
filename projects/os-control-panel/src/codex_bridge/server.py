from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from control_plane import WorkflowController


mcp = FastMCP(
    "ai-builder-os",
    instructions=(
        "Use this server to run the deterministic AI Builder OS control plane from Codex. Codex-native execution is "
        "the default and does not call the OpenAI API. Agents SDK tools are an explicit API-billed optional backend. "
        "Never expose lease tokens outside the active implementation turn."
    ),
)


def _agents_sdk_runtime():
    from agents_runtime import AgentsWorkflowRuntime

    return AgentsWorkflowRuntime()


@mcp.tool()
def list_projects() -> list[str]:
    """List projects governed by AI Builder OS product files."""
    return WorkflowController().list_projects()


@mcp.tool()
def inspect_project(project_name: str) -> dict[str, Any]:
    """Read canonical requirements, tasks, approvals, runs, and content hashes."""
    return WorkflowController().snapshot(project_name)


@mcp.tool()
def get_next_action(project_name: str) -> dict[str, Any]:
    """Return the deterministic controller's next action and role."""
    return WorkflowController().next_action(project_name).to_dict()


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
def list_pm_proposals(
    project_name: str,
    status: str = "PENDING_APPROVAL",
) -> list[dict[str, Any]]:
    """List durable PM proposals without invoking a model."""
    statuses = (status.strip().upper(),) if status.strip() else ()
    return WorkflowController().list_pm_proposals(project_name, statuses=statuses)


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
def list_codex_work_requests(
    project_name: str,
    status: str = "READY_FOR_CODEX",
) -> list[dict[str, Any]]:
    """List Codex-native work requests; pass an empty status to include every state."""
    statuses = (status,) if status.strip() else ()
    return [item.to_dict() for item in WorkflowController().list_codex_work_requests(project_name, statuses=statuses)]


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
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


@mcp.tool()
def read_product_history(project_name: str, limit: int = 50) -> list[dict[str, Any]]:
    """Read recent canonical workflow history events."""
    return WorkflowController().history(project_name, limit=min(200, max(1, limit)))


@mcp.tool()
def list_agent_approvals(project_name: str) -> list[dict[str, Any]]:
    """List optional API-backed SDK approvals without exposing serialized state or secrets."""
    return WorkflowController().snapshot(project_name)["sdk_approvals"]


@mcp.tool()
def start_agent_workflow(
    project_name: str,
    prompt: str,
    agent_name: str = "orchestrator",
    actor: str = "codex-chat",
    session_id: str = "",
) -> dict[str, Any]:
    """Explicitly run the API-billed Agents SDK backend; never use this for default Codex-native work."""
    return _agents_sdk_runtime().run(
        project_name,
        prompt,
        agent_name=agent_name,
        actor=actor,
        source="codex-mcp",
        session_id=session_id,
    )


@mcp.tool()
def resolve_agent_approval(
    project_name: str,
    run_id: str,
    approval_id: str,
    approve: bool,
    actor: str = "codex-chat",
    rejection_message: str = "",
) -> dict[str, Any]:
    """Resume one explicit API-billed SDK run after a scoped approve/reject decision."""
    return _agents_sdk_runtime().resume(
        project_name,
        run_id,
        approval_id,
        approve=approve,
        actor=actor,
        rejection_message=rejection_message,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
