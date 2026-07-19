from __future__ import annotations

from enum import StrEnum
from hashlib import sha256
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApprovalRisk(StrEnum):
    READ_ONLY = "read_only"
    REVERSIBLE_COORDINATION = "reversible_coordination"
    CANONICAL_PRODUCT_CHANGE = "canonical_product_change"
    EXTERNAL_OR_API_BILLED = "external_or_api_billed"
    DESTRUCTIVE_OR_SECRET_SENSITIVE = "destructive_or_secret_sensitive"


class ApprovalActionDescriptor(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: str = "2026-07-19.approval-action.v1"
    project_name: str = Field(min_length=1)
    action_name: str = Field(min_length=1)
    risk: ApprovalRisk
    target_type: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    target_revision: int = Field(default=0, ge=0)
    summary: str = Field(min_length=1)
    source_state: dict[str, str] = Field(default_factory=dict)
    actor_boundary: str = Field(min_length=1)
    idempotency_identity: str = Field(min_length=1)
    sealed_payload_sha256: str = Field(min_length=64, max_length=64)
    human_approval_required: bool
    external_side_effect: bool = False
    api_billing_possible: bool = False
    fallback: str = "Use explicit chat confirmation or the Streamlit Workflow Inbox."


ACTION_RISKS: dict[str, ApprovalRisk] = {
    "list_projects": ApprovalRisk.READ_ONLY,
    "inspect_project": ApprovalRisk.READ_ONLY,
    "get_next_action": ApprovalRisk.READ_ONLY,
    "get_execution_backends": ApprovalRisk.READ_ONLY,
    "get_approval_risk_policy": ApprovalRisk.READ_ONLY,
    "list_pm_proposals": ApprovalRisk.READ_ONLY,
    "describe_pm_proposal_action": ApprovalRisk.READ_ONLY,
    "list_codex_work_requests": ApprovalRisk.READ_ONLY,
    "read_product_history": ApprovalRisk.READ_ONLY,
    "list_agent_approvals": ApprovalRisk.READ_ONLY,
    "list_external_approvals": ApprovalRisk.READ_ONLY,
    "record_product_intent": ApprovalRisk.REVERSIBLE_COORDINATION,
    "submit_pm_proposal": ApprovalRisk.REVERSIBLE_COORDINATION,
    "create_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
    "create_pm_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
    "claim_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
    "resolve_codex_work_request": ApprovalRisk.REVERSIBLE_COORDINATION,
    "claim_implementation": ApprovalRisk.REVERSIBLE_COORDINATION,
    "record_implementation_evidence": ApprovalRisk.REVERSIBLE_COORDINATION,
    "approve_pm_proposal": ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
    "reject_pm_proposal": ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
    "decide_pm_proposal": ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
    "decide_external_approval": ApprovalRisk.EXTERNAL_OR_API_BILLED,
    "start_agent_workflow": ApprovalRisk.EXTERNAL_OR_API_BILLED,
    "resolve_agent_approval": ApprovalRisk.EXTERNAL_OR_API_BILLED,
}

EXTERNAL_APPROVAL_RISKS: dict[str, ApprovalRisk] = {
    "github_publication": ApprovalRisk.EXTERNAL_OR_API_BILLED,
    "release_delivery": ApprovalRisk.EXTERNAL_OR_API_BILLED,
    "repository_action": ApprovalRisk.EXTERNAL_OR_API_BILLED,
}


def approval_risk_for_action(action_name: str) -> ApprovalRisk:
    try:
        return ACTION_RISKS[action_name]
    except KeyError as exc:
        raise ValueError(f"Unknown approval action: {action_name}") from exc


def approval_risk_for_external_type(approval_type: str) -> ApprovalRisk:
    try:
        return EXTERNAL_APPROVAL_RISKS[approval_type]
    except KeyError as exc:
        raise ValueError(f"Unknown external approval type: {approval_type}") from exc


def sealed_payload_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def build_action_descriptor(
    *,
    project_name: str,
    action_name: str,
    target_type: str,
    target_id: str,
    target_revision: int,
    summary: str,
    source_state: dict[str, str],
    sealed_payload: dict[str, Any],
    actor_boundary: str = "product-director-human",
    idempotency_identity: str = "",
) -> ApprovalActionDescriptor:
    risk = approval_risk_for_action(action_name)
    if risk == ApprovalRisk.DESTRUCTIVE_OR_SECRET_SENSITIVE:
        raise PermissionError(
            "Destructive or secret-sensitive actions require a dedicated stronger manual path"
        )
    normalized_source_state = {
        str(key): str(value) for key, value in source_state.items()
    }
    normalized_actor_boundary = actor_boundary.strip()
    normalized_idempotency_identity = (
        idempotency_identity.strip()
        or f"{action_name}:{project_name}:{target_type}:{target_id}:{target_revision}"
    )
    if not all(
        (
            project_name.strip(),
            action_name.strip(),
            target_type.strip(),
            target_id.strip(),
            summary.strip(),
            normalized_actor_boundary,
            normalized_idempotency_identity,
        )
    ):
        raise ValueError("Approval action descriptors require non-empty exact-action fields")
    return ApprovalActionDescriptor(
        project_name=project_name,
        action_name=action_name,
        risk=risk,
        target_type=target_type,
        target_id=target_id,
        target_revision=target_revision,
        summary=summary.strip(),
        source_state=normalized_source_state,
        actor_boundary=normalized_actor_boundary,
        idempotency_identity=normalized_idempotency_identity,
        sealed_payload_sha256=sealed_payload_sha256(
            {
                "project_name": project_name,
                "action_name": action_name,
                "risk": risk.value,
                "target_type": target_type,
                "target_id": target_id,
                "target_revision": target_revision,
                "summary": summary.strip(),
                "source_state": normalized_source_state,
                "actor_boundary": normalized_actor_boundary,
                "idempotency_identity": normalized_idempotency_identity,
                "payload": sealed_payload,
            }
        ),
        human_approval_required=risk
        in {
            ApprovalRisk.CANONICAL_PRODUCT_CHANGE,
            ApprovalRisk.EXTERNAL_OR_API_BILLED,
            ApprovalRisk.DESTRUCTIVE_OR_SECRET_SENSITIVE,
        },
        external_side_effect=risk == ApprovalRisk.EXTERNAL_OR_API_BILLED,
        api_billing_possible=action_name in {"start_agent_workflow", "resolve_agent_approval"},
    )
