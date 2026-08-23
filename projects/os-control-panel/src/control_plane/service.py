from __future__ import annotations

import importlib
import secrets
import re
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from pm_contract import PMDecisionEnvelope, PMSourceState, PMWorkRequestPayload
from project_foundation import (
    FOUNDATION_FIELD_ORDER,
    ProjectDiscoverySession,
    ProjectFoundation,
    ProjectIdentity,
    ResearchOption,
)
from tools.project_registry import list_project_locations, resolve_project

from .approval_policy import ACTION_RISKS, EXTERNAL_APPROVAL_RISKS, build_action_descriptor
from .models import CodexWorkRequest, PMProposalRecord, WorkflowDecision, WorkPacket
from .storage import (
    append_history,
    atomic_write_json,
    atomic_write_text,
    control_data_dir,
    load_json,
    project_lock,
    project_path,
    pre_project_data_dir,
    read_history,
    sha256_file,
    utc_now,
)


def _refresh_codex_native_learning_observations(project_name: str, trigger_id: str) -> None:
    """Best-effort telemetry refresh; canonical workflow outcomes remain authoritative."""
    try:
        from system_learning import import_codex_native_history

        import_codex_native_history(project_name)
    except Exception as exc:
        try:
            from system_learning import SystemLearningStore

            SystemLearningStore(project_name)._record_detection_failure(
                "codex-native-history", trigger_id, exc
            )
        except Exception:
            pass


def _requires_mockup_first(requirement: Any) -> bool:
    """Return whether a user-facing requirement must pass the mockup gate."""
    ui_runtime = str(getattr(requirement, "ui_runtime", "") or "").strip()
    if ui_runtime not in {"web_app", "streamlit"}:
        return False
    requirement_id = str(getattr(requirement, "id", "") or "").strip()
    effort = str(getattr(requirement, "effort", "") or "").strip().upper()
    text = " ".join(
        [
            str(getattr(requirement, "title", "") or ""),
            str(getattr(requirement, "description", "") or ""),
        ]
    ).casefold()
    major_ui_markers = (
        "navigation",
        "workflow",
        "information architecture",
        "user journey",
        "layout",
        "dashboard",
        "page",
        "screen",
        "interface",
        "visual hierarchy",
    )
    return requirement_id == "R1" or effort in {"L", "XL"} or any(marker in text for marker in major_ui_markers)


def _is_mockup_approval_task(task: Any) -> bool:
    task_text = " ".join(
        [
            str(getattr(task, "title", "") or ""),
            str(getattr(task, "goal", "") or ""),
            *[str(item) for item in getattr(task, "requirements", ())],
            *[str(item) for item in getattr(task, "constraints", ())],
            *[str(item) for item in getattr(task, "validation", ())],
        ]
    ).casefold()
    has_mockup = any(marker in task_text for marker in ("mockup", "prototype", "wireframe"))
    has_human_approval = (
        any(marker in task_text for marker in ("product director", "human review", "human approval"))
        and any(marker in task_text for marker in ("approve", "approval", "accepted"))
    )
    preserves_functionality = any(
        marker in task_text
        for marker in ("functionality-preservation", "preserve functionality", "existing behavior", "existing behaviour")
    )
    return (
        str(getattr(task, "task_type", "") or "") == "Validation Task"
        and has_mockup
        and has_human_approval
        and preserves_functionality
    )


class WorkflowController:
    """Single control plane used by Streamlit, MCP, workers, and SDK agents."""

    def __init__(self) -> None:
        # Bridge a live MCP process across the R105 document-schema upgrade.
        # New bridge processes track dependencies directly; this compatibility
        # guard upgrades an older cached workspace module after imports settle.
        import workspace as workspace_module

        if not hasattr(workspace_module.RequirementDocument, "all_requirements"):
            importlib.reload(workspace_module)

    PM_RELEVANT_HISTORY_EVENTS = {
        "intent_recorded",
        "pm_proposal_approved",
        "pm_proposal_rejected",
        "pm_derived_task_plan_auto_applied",
        "implementation_evidence_recorded",
    }
    BLOCKING_BOUNDARIES = {
        "",
        "missing_input",
        "external",
        "api_billing",
        "destructive",
        "privacy",
        "secret",
        "technical",
    }

    def list_projects(self) -> list[str]:
        return [item.name for item in list_project_locations()]

    @staticmethod
    def _pre_project_session_path(session_id: str):
        clean_session_id = session_id.strip()
        if not re.fullmatch(r"[0-9a-f-]{36}", clean_session_id):
            raise ValueError("Invalid pre-project discovery session ID")
        return pre_project_data_dir() / f"{clean_session_id}.json"

    def start_project_discovery(
        self,
        identity: dict[str, Any],
        *,
        execution_backend: str = "codex_native",
    ) -> dict[str, Any]:
        session = ProjectDiscoverySession(
            execution_backend=execution_backend,
            foundation=ProjectFoundation(identity=ProjectIdentity.model_validate(identity)),
        )
        atomic_write_json(
            self._pre_project_session_path(session.session_id),
            session.model_dump(mode="json"),
        )
        return session.model_dump(mode="json")

    def get_project_discovery(self, session_id: str) -> dict[str, Any]:
        payload = load_json(self._pre_project_session_path(session_id), None)
        if payload is None:
            raise ValueError(f"Unknown pre-project discovery session: {session_id}")
        return ProjectDiscoverySession.model_validate(payload).model_dump(mode="json")

    def update_project_discovery_field(
        self,
        session_id: str,
        field: str,
        *,
        value: str = "",
        provenance: str = "user_provided",
        rationale: str = "",
    ) -> dict[str, Any]:
        path = self._pre_project_session_path(session_id)
        session = ProjectDiscoverySession.model_validate(self.get_project_discovery(session_id))
        if field not in FOUNDATION_FIELD_ORDER:
            raise ValueError(f"Unknown project-foundation field: {field}")
        if provenance == "user_provided":
            foundation = session.foundation.accept_user_answer(field, value)  # type: ignore[arg-type]
        elif provenance == "assumption_accepted":
            foundation = session.foundation.accept_assumption(field, value, rationale)  # type: ignore[arg-type]
        elif provenance == "not_applicable":
            foundation = session.foundation.mark_not_applicable(field, rationale)  # type: ignore[arg-type]
        else:
            raise ValueError("Use explicit research-option selection for research-backed values")
        updated = session.with_foundation(foundation)
        atomic_write_json(path, updated.model_dump(mode="json"))
        return updated.model_dump(mode="json")

    def offer_project_discovery_research(
        self,
        session_id: str,
        field: str,
        options: list[dict[str, Any]],
    ) -> dict[str, Any]:
        path = self._pre_project_session_path(session_id)
        session = ProjectDiscoverySession.model_validate(self.get_project_discovery(session_id))
        offered = session.offer_research(  # type: ignore[arg-type]
            field,
            [ResearchOption.model_validate(option) for option in options],
        )
        atomic_write_json(path, offered.model_dump(mode="json"))
        return offered.model_dump(mode="json")

    def select_project_discovery_research(
        self,
        session_id: str,
        field: str,
        option_id: str,
    ) -> dict[str, Any]:
        path = self._pre_project_session_path(session_id)
        session = ProjectDiscoverySession.model_validate(self.get_project_discovery(session_id))
        selected = session.select_research(field, option_id)  # type: ignore[arg-type]
        atomic_write_json(path, selected.model_dump(mode="json"))
        return selected.model_dump(mode="json")

    def prepare_pre_project_proposal(self, session_id: str) -> dict[str, Any]:
        path = self._pre_project_session_path(session_id)
        session = ProjectDiscoverySession.model_validate(self.get_project_discovery(session_id))
        revision = session.proposal.revision + 1 if session.proposal is not None else 1
        prepared = session.prepare_proposal(revision=revision)
        atomic_write_json(path, prepared.model_dump(mode="json"))
        return prepared.model_dump(mode="json")

    def approve_pre_project_proposal(
        self,
        session_id: str,
        *,
        exact_seal: str,
        actor: str,
    ) -> dict[str, Any]:
        path = self._pre_project_session_path(session_id)
        session = ProjectDiscoverySession.model_validate(self.get_project_discovery(session_id))
        approved = session.approve(exact_seal=exact_seal, actor=actor)
        atomic_write_json(path, approved.model_dump(mode="json"))
        return approved.model_dump(mode="json")

    def snapshot(self, project_name: str) -> dict[str, Any]:
        from workspace import active_approvals, list_implementation_runs, load_requirement_document, load_task_document

        location = resolve_project(project_name)
        root = location.workspace_path
        memory_path = root / "memory.md"
        if not memory_path.exists():
            memory_path = root / "product" / "memory.md"
        pending_sdk_runs = load_json(control_data_dir(project_name) / "pending_agent_runs.json", [])
        requirements = load_requirement_document(project_name)
        tasks = load_task_document(project_name)
        return {
            "project_name": project_name,
            "project_id": location.project_id,
            "project_location": {
                "name": location.name,
                "display_name": location.display_name,
                "mode": location.mode,
                "visibility": location.visibility,
                "ownership": location.ownership,
                "repository": location.repository if location.visibility == "public" else "",
                "default_branch": location.default_branch,
                "external": location.is_external,
            },
            "requirements": [asdict(item) for item in requirements.all_requirements],
            "tasks": [asdict(item) for item in tasks.tasks],
            "approvals": [asdict(item) for item in active_approvals(project_name)],
            "sdk_approvals": [
                {
                    "run_id": item.get("run_id", ""),
                    "trace_id": item.get("trace_id", ""),
                    "source": item.get("source", ""),
                    "created_at": item.get("created_at", ""),
                    "approvals": item.get("approvals", []),
                }
                for item in pending_sdk_runs
                if item.get("status") == "AWAITING_APPROVAL"
            ],
            "implementation_runs": [asdict(item) for item in list_implementation_runs(project_name)[:10]],
            "codex_work_requests": [item.to_dict() for item in self.list_codex_work_requests(project_name)[:20]],
            "pm_proposals": self.list_pm_proposals(
                project_name,
                statuses=("PENDING_APPROVAL", "NEEDS_INPUT"),
            )[:20],
            "canonical_hashes": {
                "requirements": sha256_file(root / "product" / "requirements.md"),
                "tasks": sha256_file(root / "product" / "tasks.md"),
                "memory": sha256_file(memory_path),
            },
        }

    def create_codex_work_request(
        self,
        project_name: str,
        task: str,
        *,
        requested_by: str,
        source: str,
        requested_role: str = "engineer",
        requirement_id: str = "",
        idempotency_key: str = "",
        request_kind: str = "general",
        payload: dict[str, Any] | None = None,
    ) -> CodexWorkRequest:
        clean_task = " ".join(task.split()).strip()
        if not clean_task:
            raise ValueError("task must not be empty")
        if len(clean_task) > 12_000:
            raise ValueError("task must be 12000 characters or fewer")
        role = requested_role.strip().lower().replace(" ", "_") or "engineer"
        allowed_roles = {
            "orchestrator",
            "pm",
            "experience_designer",
            "ui_designer",
            "architect",
            "engineer",
            "qa",
            "learning_agent",
            "os_learning_agent",
        }
        if role not in allowed_roles:
            raise ValueError(f"Unsupported Codex role: {requested_role}")
        requirement_id = requirement_id.strip()
        request_kind = request_kind.strip() or "general"
        if request_kind not in {"general", "pm_decision", "implementation", "os_learning_diagnosis"}:
            raise ValueError(f"Unsupported Codex work-request kind: {request_kind}")
        structured_payload = dict(payload or {})
        if request_kind == "general" and structured_payload:
            raise ValueError("General Codex work requests cannot contain a structured payload")
        if request_kind == "implementation":
            task_numbers = structured_payload.get("task_numbers", [])
            if not requirement_id or role != "engineer":
                raise ValueError("Implementation requests require an Engineer and requirement ID")
            if (
                not isinstance(task_numbers, list)
                or not task_numbers
                or any(not isinstance(item, int) or item <= 0 for item in task_numbers)
            ):
                raise ValueError("Implementation requests require positive task numbers")
        if request_kind == "os_learning_diagnosis":
            expected_keys = {"signal_id", "capability_id", "cadence", "read_only", "namespace"}
            if role != "os_learning_agent" or requirement_id:
                raise ValueError("OS-learning diagnosis requests require the read-only OS Learning Agent")
            if set(structured_payload) != expected_keys:
                raise ValueError("OS-learning diagnosis payload has an invalid shape")
            if not str(structured_payload.get("signal_id", "")).strip():
                raise ValueError("OS-learning diagnosis requires a signal ID")
            if not str(structured_payload.get("capability_id", "")).strip():
                raise ValueError("OS-learning diagnosis requires a capability ID")
            if structured_payload.get("cadence") not in {"fast", "slow"}:
                raise ValueError("OS-learning diagnosis requires a supported cadence")
            if structured_payload.get("read_only") is not True:
                raise ValueError("OS-learning diagnosis must retain the read-only boundary")
            namespace = str(structured_payload.get("namespace", "")).strip()
            if not namespace or not re.fullmatch(r"[a-z0-9]+(?:[._-][a-z0-9]+)*", namespace):
                raise ValueError("OS-learning diagnosis requires a safe evidence namespace")
        if requirement_id:
            from workspace import load_requirement_document

            document = load_requirement_document(project_name)
            known_ids = {item.id for item in document.all_requirements}
            if requirement_id not in known_ids:
                raise ValueError(f"Unknown requirement: {requirement_id}")

        store_path = control_data_dir(project_name) / "codex_work_requests.json"
        with project_lock(project_name):
            requests = load_json(store_path, [])
            if idempotency_key:
                previous = next(
                    (item for item in requests if item.get("idempotency_key") == idempotency_key),
                    None,
                )
                if previous:
                    return self._codex_work_request_from_dict(previous)
            request = CodexWorkRequest(
                request_id=str(uuid4()),
                project_name=project_name,
                task=clean_task,
                requested_role=role,
                requirement_id=requirement_id,
                status="READY_FOR_CODEX",
                requested_by=requested_by.strip() or "unknown",
                source=source.strip() or "unknown",
                created_at=utc_now(),
                request_kind=request_kind,
                payload=structured_payload,
            )
            requests.append(request.to_dict() | {"idempotency_key": idempotency_key})
            atomic_write_json(store_path, requests)
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "codex_work_requested",
                "actor": request.requested_by,
                "source": request.source,
                "request_id": request.request_id,
                "requirement_id": requirement_id,
                "requested_role": role,
                "task": clean_task,
                "request_kind": request_kind,
                "idempotency_key": f"codex-work:{idempotency_key}" if idempotency_key else "",
            },
        )
        return request

    def create_pm_codex_work_request(
        self,
        project_name: str,
        payload: PMWorkRequestPayload | dict[str, Any],
        *,
        requested_by: str,
        source: str,
        idempotency_key: str = "",
    ) -> CodexWorkRequest:
        request_payload = (
            PMWorkRequestPayload.model_validate(payload.model_dump(mode="json"))
            if isinstance(payload, PMWorkRequestPayload)
            else PMWorkRequestPayload.model_validate(payload)
        )
        self._validate_pm_work_request(project_name, request_payload)
        targets = ", ".join(request_payload.target_requirement_ids)
        action = {
            "prioritisation": "prioritise",
            "task_plan": "plan tasks for",
            "artifact_review": "review artifact",
            "outcome_review": "review delivered outcome for",
        }[request_payload.mode]
        task = (
            f"Run the canonical PM {request_payload.mode} mode to {action} {targets}. "
            "Read fresh project state, return one PMDecisionEnvelope, submit it with this work request as its origin, "
            "and resolve this queue item with the resulting proposal ID and revision."
        )
        return self.create_codex_work_request(
            project_name,
            task,
            requested_by=requested_by,
            source=source,
            requested_role="pm",
            requirement_id=(
                request_payload.target_requirement_ids[0]
                if request_payload.mode in {"task_plan", "outcome_review"}
                else ""
            ),
            idempotency_key=idempotency_key,
            request_kind="pm_decision",
            payload=request_payload.model_dump(mode="json"),
        )

    def list_codex_work_requests(
        self,
        project_name: str,
        *,
        statuses: tuple[str, ...] = (),
    ) -> list[CodexWorkRequest]:
        values = load_json(control_data_dir(project_name) / "codex_work_requests.json", [])
        allowed = {status.upper() for status in statuses}
        requests = [self._codex_work_request_from_dict(item) for item in values]
        if allowed:
            requests = [item for item in requests if item.status in allowed]
        return sorted(requests, key=lambda item: item.created_at, reverse=True)

    def claim_codex_work_request(
        self,
        project_name: str,
        request_id: str,
        *,
        actor: str,
        lease_minutes: int = 240,
    ) -> CodexWorkRequest:
        if lease_minutes < 5 or lease_minutes > 480:
            raise ValueError("lease_minutes must be between 5 and 480")
        store_path = control_data_dir(project_name) / "codex_work_requests.json"
        with project_lock(project_name):
            requests = load_json(store_path, [])
            matching = next((item for item in requests if item.get("request_id") == request_id), None)
            if matching is None:
                raise ValueError(f"Unknown Codex work request: {request_id}")
            now = datetime.now(timezone.utc)
            claim_expires_at = str(matching.get("claim_expires_at", ""))
            stale_claim = False
            if matching.get("status") == "CLAIMED_BY_CODEX" and claim_expires_at:
                try:
                    stale_claim = datetime.fromisoformat(claim_expires_at) <= now
                except ValueError:
                    stale_claim = False
            if matching.get("status") != "READY_FOR_CODEX" and not stale_claim:
                raise ValueError(f"Codex work request is already {matching.get('status')}")
            matching["status"] = "CLAIMED_BY_CODEX"
            matching["claimed_by"] = actor.strip() or "codex-chat"
            matching["claimed_at"] = now.isoformat()
            matching["claim_expires_at"] = (now + timedelta(minutes=lease_minutes)).isoformat()
            atomic_write_json(store_path, requests)
            request = self._codex_work_request_from_dict(matching)
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "codex_work_claimed",
                "actor": request.claimed_by,
                "request_id": request.request_id,
                "requirement_id": request.requirement_id,
                "requested_role": request.requested_role,
            },
        )
        return request

    def resolve_codex_work_request(
        self,
        project_name: str,
        request_id: str,
        *,
        actor: str,
        status: str,
        summary: str,
        implementation_run_id: str = "",
        result_proposal_id: str = "",
        result_proposal_revision: int = 0,
    ) -> CodexWorkRequest:
        terminal_status = status.strip().upper()
        if terminal_status not in {"COMPLETED", "BLOCKED", "FAILED", "CANCELLED"}:
            raise ValueError("status must be COMPLETED, BLOCKED, FAILED, or CANCELLED")
        clean_summary = " ".join(summary.split()).strip()
        if not clean_summary:
            raise ValueError("summary must not be empty")
        store_path = control_data_dir(project_name) / "codex_work_requests.json"
        with project_lock(project_name):
            requests = load_json(store_path, [])
            matching = next((item for item in requests if item.get("request_id") == request_id), None)
            if matching is None:
                raise ValueError(f"Unknown Codex work request: {request_id}")
            if matching.get("status") not in {"READY_FOR_CODEX", "CLAIMED_BY_CODEX"}:
                raise ValueError(f"Codex work request is already {matching.get('status')}")
            clean_proposal_id = result_proposal_id.strip()
            if bool(clean_proposal_id) != (result_proposal_revision > 0):
                raise ValueError("Proposal result ID and revision must be provided together")
            if matching.get("request_kind", "general") == "pm_decision":
                if terminal_status == "COMPLETED" and (
                    not clean_proposal_id or result_proposal_revision <= 0
                ):
                    raise ValueError("PM Codex work requests require a resulting proposal ID and revision")
                if clean_proposal_id or result_proposal_revision:
                    proposals = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
                    proposal = self._find_pm_proposal(proposals, clean_proposal_id, result_proposal_revision)
                    if proposal.get("origin_request_id") != request_id:
                        raise ValueError("PM proposal does not belong to this Codex work request")
            elif clean_proposal_id or result_proposal_revision:
                raise ValueError("Only PM Codex work requests may resolve with a proposal result")
            matching["status"] = terminal_status
            matching["resolved_at"] = utc_now()
            matching["summary"] = clean_summary
            matching["implementation_run_id"] = implementation_run_id.strip()
            matching["result_proposal_id"] = clean_proposal_id
            matching["result_proposal_revision"] = result_proposal_revision
            atomic_write_json(store_path, requests)
            request = self._codex_work_request_from_dict(matching)
        resolved_event = append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "codex_work_resolved",
                "actor": actor.strip() or "codex-chat",
                "request_id": request.request_id,
                "requirement_id": request.requirement_id,
                "status": terminal_status,
                "summary": clean_summary,
                "implementation_run_id": request.implementation_run_id,
                "result_proposal_id": request.result_proposal_id,
                "result_proposal_revision": request.result_proposal_revision,
            },
        )
        _refresh_codex_native_learning_observations(
            project_name, str(resolved_event.get("event_id", request.request_id))
        )
        return request

    @staticmethod
    def _codex_work_request_from_dict(payload: dict[str, Any]) -> CodexWorkRequest:
        return CodexWorkRequest(
            request_id=str(payload.get("request_id", "")),
            project_name=str(payload.get("project_name", "")),
            task=str(payload.get("task", "")),
            requested_role=str(payload.get("requested_role", "")),
            requirement_id=str(payload.get("requirement_id", "")),
            status=str(payload.get("status", "")),
            requested_by=str(payload.get("requested_by", "")),
            source=str(payload.get("source", "")),
            created_at=str(payload.get("created_at", "")),
            claimed_by=str(payload.get("claimed_by", "")),
            claimed_at=str(payload.get("claimed_at", "")),
            claim_expires_at=str(payload.get("claim_expires_at", "")),
            resolved_at=str(payload.get("resolved_at", "")),
            summary=str(payload.get("summary", "")),
            implementation_run_id=str(payload.get("implementation_run_id", "")),
            request_kind=str(payload.get("request_kind", "general") or "general"),
            payload=dict(payload.get("payload", {})) if isinstance(payload.get("payload", {}), dict) else {},
            result_proposal_id=str(payload.get("result_proposal_id", "")),
            result_proposal_revision=int(payload.get("result_proposal_revision", 0) or 0),
        )

    def _validate_pm_work_request(
        self,
        project_name: str,
        payload: PMWorkRequestPayload,
    ) -> None:
        from workspace import load_requirement_document

        document = load_requirement_document(project_name)
        requirements = {
            item.id: item for item in document.all_requirements
        }
        unknown = [
            item
            for item in payload.target_requirement_ids
            if payload.mode != "artifact_review" and item not in requirements
        ]
        if unknown:
            raise ValueError(f"Unknown PM work-request requirements: {', '.join(unknown)}")
        if payload.mode == "prioritisation":
            in_progress = [item.id for item in requirements.values() if item.status == "IN_PROGRESS"]
            if in_progress:
                raise ValueError(
                    f"Prioritisation cannot activate new work while {', '.join(in_progress)} is IN_PROGRESS"
                )
            ineligible = [
                item for item in payload.target_requirement_ids if requirements[item].status != "NEW"
            ]
            if ineligible:
                raise ValueError(
                    f"Prioritisation targets must be NEW: {', '.join(ineligible)}"
                )
        elif payload.mode == "task_plan":
            target = requirements[payload.target_requirement_ids[0]]
            active_ids = [item.id for item in requirements.values() if item.status == "IN_PROGRESS"]
            if target.status != "IN_PROGRESS" or active_ids != [target.id]:
                raise ValueError("Task planning requires one IN_PROGRESS requirement")
            if payload.authorization_proposal_id:
                self._validate_requirement_authorization(
                    project_name,
                    target.id,
                    payload.authorization_proposal_id,
                    payload.authorization_proposal_revision,
                )
        elif payload.mode == "artifact_review":
            from workspace import list_approvals

            artifact_id = payload.target_requirement_ids[0]
            artifact = next(
                (item for item in list_approvals(project_name) if item.approval_id == artifact_id),
                None,
            )
            if artifact is None or artifact.status != "APPROVED":
                raise ValueError("Artifact review requires one approved workflow artifact")

        if payload.parent_proposal_id:
            proposals = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
            parent = self._find_pm_proposal(
                proposals,
                payload.parent_proposal_id,
                payload.parent_proposal_revision,
            )
            if parent.get("status") != "NEEDS_INPUT":
                raise ValueError("A PM continuation must reference a NEEDS_INPUT proposal")
            parent_decision = PMDecisionEnvelope.model_validate(parent.get("proposal", {}))
            if parent_decision.mode != payload.mode:
                raise ValueError("PM continuation mode must match its parent proposal")
            if not payload.operator_context.strip():
                raise ValueError("PM continuation requires an operator answer")

    def next_action(self, project_name: str) -> WorkflowDecision:
        from workspace import (
            active_approvals,
            load_requirement_document,
            load_task_document,
            orchestrator_recommendation,
        )

        pending_proposals = self.list_pm_proposals(project_name, statuses=("PENDING_APPROVAL",))
        if pending_proposals:
            proposal = pending_proposals[0]
            return WorkflowDecision(
                project_name=project_name,
                next_action=(
                    f"Review requirement proposal {proposal['proposal_id']} "
                    f"revision {proposal['proposal_revision']}."
                ),
                next_role="Product Director",
                why="The workflow is waiting only at the requirement approval boundary.",
            )
        queued = self.list_codex_work_requests(
            project_name,
            statuses=("READY_FOR_CODEX", "CLAIMED_BY_CODEX"),
        )
        if queued:
            request = queued[-1]
            waiting = request.status == "READY_FOR_CODEX"
            return WorkflowDecision(
                project_name=project_name,
                next_action=(
                    f"Claim and continue Codex work request {request.request_id}."
                    if waiting
                    else f"Continue claimed Codex work request {request.request_id}."
                ),
                next_role=(
                    "OS Learning Agent"
                    if request.requested_role == "os_learning_agent"
                    else request.requested_role.replace("_", " ").title()
                ),
                why=(
                    "Approved work is durably queued and waiting for an active Codex host."
                    if waiting
                    else "The approved workflow is already running under a bounded Codex claim."
                ),
            )
        requirements = load_requirement_document(project_name)
        active = [
            item
            for item in requirements.all_requirements
            if item.status == "IN_PROGRESS"
        ]
        if len(active) == 1:
            blocked = self._latest_blocked_run(project_name, active[0].id)
            if blocked is not None:
                evidence = blocked.get("evidence", {})
                boundary = str(evidence.get("blocking_boundary", "") or "technical")
                reason = str(evidence.get("blocking_reason", "")).strip()
                remaining = evidence.get("remaining_task_numbers", [])
                task_label = (
                    f" Remaining tasks: {', '.join(str(item) for item in remaining)}."
                    if remaining
                    else ""
                )
                return WorkflowDecision(
                    project_name=project_name,
                    next_action=f"Resolve the {boundary.replace('_', ' ')} blocker for {active[0].id}.",
                    next_role="Product Director" if boundary != "technical" else "Engineer",
                    why=(reason or str(evidence.get("summary", "")).strip() or "Delivery is blocked.") + task_label,
                )
        recommendation = orchestrator_recommendation(project_name)
        if len(active) == 1 and recommendation.next_role in {
            "Architect",
            "Experience Designer",
            "UI Designer",
            "QA",
        }:
            completed_roles = self._completed_specialist_roles(project_name, active[0].id)
            if recommendation.next_role in completed_roles:
                pending = [
                    item
                    for item in load_task_document(project_name).tasks
                    if active[0].id in item.requirements and item.status in {"TODO", "IN_PROGRESS"}
                ]
                if pending:
                    first = pending[0]
                    return WorkflowDecision(
                        project_name=project_name,
                        next_action=f"Run Engineer on Task {first.number}.",
                        next_role="Engineer",
                        why=(
                            f"The {recommendation.next_role} gate is already satisfied by durable evidence "
                            f"for {active[0].id}; Task {first.number} remains {first.status}."
                        ),
                    )
        approvals = active_approvals(project_name)
        return WorkflowDecision(
            project_name=project_name,
            next_action=recommendation.next_action,
            next_role=recommendation.next_role,
            why=recommendation.why,
            blocking_approval_ids=tuple(item.approval_id for item in approvals),
        )

    def _latest_blocked_run(self, project_name: str, requirement_id: str) -> dict[str, Any] | None:
        runs = load_json(control_data_dir(project_name) / "interactive_runs.json", [])
        terminal = [
            item
            for item in runs
            if item.get("requirement_id") == requirement_id
            and item.get("status") in {"COMPLETED", "BLOCKED", "FAILED"}
        ]
        if not terminal:
            return None
        latest = max(
            terminal,
            key=lambda item: str(item.get("completed_at", "") or item.get("claimed_at", "")),
        )
        return latest if latest.get("status") == "BLOCKED" else None

    def _completed_specialist_roles(self, project_name: str, requirement_id: str) -> set[str]:
        role_names = {
            "architect": "Architect",
            "experience_designer": "Experience Designer",
            "ui_designer": "UI Designer",
            "qa": "QA",
        }
        completed: set[str] = set()
        approved = [
            item
            for item in self.list_pm_proposals(project_name, statuses=("APPROVED",))
            if any(
                change.get("requirement_id") == requirement_id
                for change in item.get("proposal", {}).get("requirement_changes", [])
            )
        ]
        latest_approval = max(
            approved,
            key=lambda item: str(item.get("resolved_at", "")),
            default=None,
        )
        if latest_approval is not None:
            completed.update(
                str(item.get("role", ""))
                for item in latest_approval.get("proposal", {}).get("consultations", [])
                if str(item.get("role", "")) in role_names.values()
            )
            approved_at = str(latest_approval.get("resolved_at", ""))
        else:
            approved_at = ""
        for request in self.list_codex_work_requests(project_name):
            if (
                request.requirement_id == requirement_id
                and request.status == "COMPLETED"
                and request.requested_role in role_names
                and (not approved_at or request.resolved_at >= approved_at)
            ):
                completed.add(role_names[request.requested_role])
        return completed

    def _validate_requirement_authorization(
        self,
        project_name: str,
        requirement_id: str,
        proposal_id: str,
        proposal_revision: int,
    ) -> PMDecisionEnvelope:
        records = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
        record = self._find_pm_proposal(records, proposal_id, proposal_revision)
        if record.get("status") != "APPROVED":
            raise ValueError("Derived work requires an approved requirement proposal")
        decision = PMDecisionEnvelope.model_validate(record.get("proposal", {}))
        matching = [
            change
            for change in decision.requirement_changes
            if change.requirement_id == requirement_id and change.status == "IN_PROGRESS"
        ]
        if decision.mode != "requirement_draft" or len(matching) != 1:
            raise ValueError("Proposal does not authorize this active requirement")
        return decision

    def ensure_autonomous_progress(
        self,
        project_name: str,
        *,
        requirement_id: str = "",
        authorization_proposal_id: str = "",
        authorization_proposal_revision: int = 0,
        retry_identity: str = "",
        retry_authorization_id: str = "",
    ) -> dict[str, Any]:
        """Materialize the next model-free queue transition for approved internal work."""
        from workspace import load_requirement_document, load_task_document

        requirements = load_requirement_document(project_name)
        active = [
            item
            for item in requirements.all_requirements
            if item.status == "IN_PROGRESS"
        ]
        if requirement_id:
            active = [item for item in active if item.id == requirement_id]
        if len(active) != 1:
            return {
                "state": "IDLE" if not active else "BLOCKED",
                "requirement_id": requirement_id,
                "detail": "Autonomous delivery requires exactly one active requirement.",
            }
        target = active[0]
        authorization = None
        if authorization_proposal_id:
            authorization = self._validate_requirement_authorization(
                project_name,
                target.id,
                authorization_proposal_id,
                authorization_proposal_revision,
            )
        else:
            approved = self.list_pm_proposals(project_name, statuses=("APPROVED",))
            for record in approved:
                decision = PMDecisionEnvelope.model_validate(record.get("proposal", {}))
                if any(
                    change.requirement_id == target.id and change.status == "IN_PROGRESS"
                    for change in decision.requirement_changes
                ):
                    authorization_proposal_id = str(record["proposal_id"])
                    authorization_proposal_revision = int(record["proposal_revision"])
                    authorization = self._validate_requirement_authorization(
                        project_name,
                        target.id,
                        authorization_proposal_id,
                        authorization_proposal_revision,
                    )
                    break
        if authorization is None:
            return {
                "state": "WAITING_FOR_REQUIREMENT_APPROVAL",
                "requirement_id": target.id,
                "detail": "The active requirement has no exact approved requirement authorization.",
            }

        all_tasks = load_task_document(project_name).tasks
        linked = [item for item in all_tasks if target.id in item.requirements]
        pending = [item for item in linked if item.status in {"TODO", "IN_PROGRESS"}]
        queued = [
            item
            for item in self.list_codex_work_requests(project_name)
            if item.requirement_id == target.id
            and item.status in {"READY_FOR_CODEX", "CLAIMED_BY_CODEX"}
        ]
        if queued:
            request = sorted(queued, key=lambda item: item.created_at)[0]
            return {
                "state": "QUEUED_FOR_CODEX" if request.status == "READY_FOR_CODEX" else "RUNNING",
                "requirement_id": target.id,
                "request": request.to_dict(),
                "detail": "Approved internal work already has one durable Codex request.",
            }
        if not linked:
            payload = PMWorkRequestPayload(
                mode="task_plan",
                target_requirement_ids=[target.id],
                operator_context=(
                    "Derive bounded internal delivery tasks from the exact approved requirement. "
                    "The controller may apply a valid plan without another product approval."
                ),
                authorization_proposal_id=authorization_proposal_id,
                authorization_proposal_revision=authorization_proposal_revision,
            )
            request = self.create_pm_codex_work_request(
                project_name,
                payload,
                requested_by="deterministic-controller",
                source="controller-autonomous",
                idempotency_key=(
                    f"autonomous-task-plan:{target.id}:"
                    f"{authorization_proposal_id}:{authorization_proposal_revision}"
                ),
            )
            return {
                "state": "QUEUED_FOR_CODEX",
                "requirement_id": target.id,
                "request": request.to_dict(),
                "detail": "Task planning was queued automatically from requirement approval.",
            }
        if pending:
            task_numbers = sorted(item.number for item in pending)
            blocked_run = self._latest_blocked_run(project_name, target.id)
            has_retry_identity = bool(retry_identity.strip())
            has_retry_authorization = bool(retry_authorization_id.strip())
            if has_retry_identity != has_retry_authorization:
                raise ValueError(
                    "A blocked retry requires both a new retry identity and exact authorization ID"
                )
            if blocked_run is not None and not has_retry_identity:
                evidence = blocked_run.get("evidence", {})
                return {
                    "state": "BLOCKED",
                    "requirement_id": target.id,
                    "blocking_boundary": str(
                        evidence.get("blocking_boundary", "") or "technical"
                    ),
                    "blocking_reason": str(
                        evidence.get("blocking_reason", "")
                        or evidence.get("summary", "")
                        or "Delivery is blocked."
                    ),
                    "remaining_task_numbers": task_numbers,
                    "implementation_run_id": str(blocked_run.get("run_id", "")),
                    "detail": (
                        "A terminal blocked implementation remains unresolved. "
                        "Provide a new exact authorization and retry identity before queueing another attempt."
                    ),
                }
            if blocked_run is not None:
                prior_evidence = blocked_run.get("evidence", {})
                if retry_identity.strip() == str(prior_evidence.get("retry_identity", "")):
                    raise ValueError("A blocked retry must use a new retry identity")
                if retry_authorization_id.strip() == str(
                    prior_evidence.get("retry_authorization_id", "")
                ):
                    raise ValueError("A blocked retry must use a new exact authorization ID")
            request = self.create_codex_work_request(
                project_name,
                (
                    f"Implement approved requirement {target.id} across Tasks "
                    f"{', '.join(str(item) for item in task_numbers)}. Continue through proportionate "
                    "specialist checks, implementation, tests, QA, evidence, and canonical reconciliation. "
                    "Stop only for a genuine blocker or separately governed external/high-risk action."
                ),
                requested_by="deterministic-controller",
                source="controller-autonomous",
                requested_role="engineer",
                requirement_id=target.id,
                idempotency_key=(
                    f"autonomous-implementation:{target.id}:"
                    + "-".join(str(item) for item in task_numbers)
                    + (f":retry:{retry_identity.strip()}" if retry_identity.strip() else "")
                ),
                request_kind="implementation",
                payload={
                    "task_numbers": task_numbers,
                    "authorization_proposal_id": authorization_proposal_id,
                    "authorization_proposal_revision": authorization_proposal_revision,
                    "retry_identity": retry_identity.strip(),
                    "retry_authorization_id": retry_authorization_id.strip(),
                },
            )
            return {
                "state": "QUEUED_FOR_CODEX",
                "requirement_id": target.id,
                "request": request.to_dict(),
                "detail": "Implementation was queued automatically from approved derived tasks.",
            }
        return {
            "state": "READY_TO_COMPLETE",
            "requirement_id": target.id,
            "detail": "All linked tasks are terminal; completion evidence can reconcile the requirement.",
        }

    def build_pm_review_evidence(
        self,
        project_name: str,
        review_mode: str,
        target_id: str,
    ) -> dict[str, Any]:
        from pm_evidence import build_pm_mode_evidence
        from pm_review import build_pm_review_evidence

        source_state = self._pm_source_state(project_name)
        mode_evidence = (
            build_pm_mode_evidence(
                project_name,
                "outcome_review",
                [target_id],
                source_state,
            )
            if review_mode == "outcome_review"
            else None
        )
        return build_pm_review_evidence(
            project_name,
            review_mode,
            target_id,
            mode_evidence=mode_evidence,
            source_state=source_state.model_copy(update={"history_event_id": ""}),
        ).model_dump(mode="json")

    def build_pm_evidence_packet(
        self,
        project_name: str,
        mode: str,
        target_requirement_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build mode-aware first-party evidence without invoking a model."""
        from pm_evidence import build_pm_mode_evidence

        if mode not in {
            "discovery",
            "requirement_draft",
            "prioritisation",
            "task_plan",
            "artifact_review",
            "outcome_review",
        }:
            raise ValueError(f"Unsupported PM mode: {mode}")
        return build_pm_mode_evidence(
            project_name,
            mode,  # type: ignore[arg-type]
            target_requirement_ids or [],
            self._pm_source_state(project_name),
        ).model_dump(mode="json")

    def preflight_pm_proposal(
        self,
        project_name: str,
        proposal: PMDecisionEnvelope | dict[str, Any],
    ) -> dict[str, Any]:
        """Validate a PM decision without persisting, applying, or reserving identifiers."""
        source_state = self._pm_source_state(project_name)
        findings: list[dict[str, Any]] = []
        try:
            decision = (
                PMDecisionEnvelope.model_validate(proposal.model_dump(mode="json"))
                if isinstance(proposal, PMDecisionEnvelope)
                else PMDecisionEnvelope.model_validate(proposal)
            )
            if decision.project_name and decision.project_name != project_name:
                raise ValueError("PM proposal project does not match the controller project")
            decision = self._materialize_pm_proposal_ids(
                project_name,
                decision.model_copy(update={"project_name": project_name, "source_state": source_state}),
            )
            from pm_guardrails import collect_pm_guardrail_findings

            quality_findings = collect_pm_guardrail_findings(project_name, decision)
            findings = [item.model_dump(mode="json") for item in quality_findings]
            blocking = [item for item in quality_findings if item.severity == "blocking"]
            if blocking:
                raise ValueError("; ".join(f"{item.code}: {item.message}" for item in blocking))
            self._validate_pm_proposal(project_name, decision, include_quality_guardrails=False)
            if decision.work_request is not None:
                self._validate_pm_work_request(project_name, decision.work_request)
                self._validate_pm_proposal_against_work_request(decision, decision.work_request)
        except (TypeError, ValueError) as exc:
            valid = False
            errors = [str(exc)]
            mode = str(proposal.get("mode", "")) if isinstance(proposal, dict) else proposal.mode
        else:
            valid = True
            errors = []
            mode = decision.mode
        from agents_runtime.support import pm_mode_tool_names

        return {
            "valid": valid,
            "errors": errors,
            "findings": findings,
            "source_state": source_state.model_dump(mode="json"),
            "mode": mode,
            "allowed_tools": list(pm_mode_tool_names(mode)) if mode else [],
            "persisted": False,
        }

    def record_intent(
        self,
        project_name: str,
        intent: str,
        *,
        actor: str,
        source: str,
        idempotency_key: str = "",
    ) -> dict[str, Any]:
        clean = " ".join(intent.split()).strip()
        if not clean:
            raise ValueError("intent must not be empty")
        if len(clean) > 4000:
            raise ValueError("intent must be 4000 characters or fewer")
        if idempotency_key:
            existing = next(
                (event for event in reversed(read_history(project_name, limit=500)) if event.get("idempotency_key") == idempotency_key),
                None,
            )
            if existing:
                return existing
        return append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "intent_recorded",
                "actor": actor,
                "source": source,
                "intent": clean,
                "idempotency_key": idempotency_key,
            },
        )

    def retire_requirement(
        self,
        project_name: str,
        requirement_id: str,
        *,
        reason: str,
        actor: str,
        authorization: str,
        idempotency_key: str = "",
    ) -> dict[str, Any]:
        from workspace import load_requirement_document, retire_requirement

        clean_reason = " ".join(reason.split()).strip()
        clean_actor = " ".join(actor.split()).strip()
        clean_authorization = " ".join(authorization.split()).strip()
        if not clean_reason or not clean_actor or not clean_authorization:
            raise ValueError("Retirement requires reason, actor, and authorization")
        key = idempotency_key or f"requirement-retired:{requirement_id}:{clean_authorization}"
        existing_event = next(
            (event for event in reversed(read_history(project_name, limit=1000)) if event.get("idempotency_key") == key),
            None,
        )
        if existing_event is not None:
            return existing_event

        current = next(
            (item for item in load_requirement_document(project_name).all_requirements if item.id == requirement_id),
            None,
        )
        if current is None:
            raise ValueError(f"Requirement not found: {requirement_id}")
        if current.status == "RETIRED":
            raise ValueError(f"Retired requirement is missing its canonical idempotency event: {requirement_id}")

        retired_at = utc_now()
        result = retire_requirement(
            project_name,
            requirement_id,
            reason=clean_reason,
            actor=clean_actor,
            retired_at=retired_at,
            authorization=clean_authorization,
        )
        return append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "requirement_retired",
                "actor": clean_actor,
                "source": "deterministic-controller",
                "requirement_id": requirement_id,
                "reason": clean_reason,
                "retired_at": retired_at,
                "authorization": clean_authorization,
                "retired_tasks": result.retired_tasks,
                "updated_tasks": result.updated_tasks,
                "preserved_done_tasks": result.preserved_done_tasks,
                "idempotency_key": key,
            },
        )

    def list_pm_proposals(
        self,
        project_name: str,
        *,
        statuses: tuple[str, ...] = (),
    ) -> list[dict[str, Any]]:
        values = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
        allowed = {status.strip().upper() for status in statuses}
        if allowed:
            values = [item for item in values if str(item.get("status", "")).upper() in allowed]
        return sorted(
            [dict(item) for item in values if isinstance(item, dict)],
            key=lambda item: (str(item.get("submitted_at", "")), int(item.get("proposal_revision", 0))),
            reverse=True,
        )

    def approval_risk_policy(self) -> dict[str, Any]:
        return {
            "tools": {
                action_name: risk.value
                for action_name, risk in sorted(ACTION_RISKS.items())
            },
            "external_approval_types": {
                approval_type: risk.value
                for approval_type, risk in sorted(EXTERNAL_APPROVAL_RISKS.items())
            },
            "unknown_action_policy": "fail_closed",
            "destructive_or_secret_sensitive_policy": "dedicated_manual_path_only",
            "requirement_authorization": {
                "human_gate": "one exact requirement proposal revision",
                "derived_task_plan": (
                    "controller-applied without another human gate only when the typed work request "
                    "carries a valid exact approved active-requirement authorization"
                ),
                "implementation_and_qa": "reversible coordination under the same bounded authorization lineage",
                "external_and_api_billed": "separate exact human authorization remains required",
            },
        }

    def describe_pm_proposal_action(
        self,
        project_name: str,
        proposal_id: str,
        proposal_revision: int,
        *,
        decision: str,
    ) -> dict[str, Any]:
        clean_decision = decision.strip().lower()
        if clean_decision not in {"approve", "reject"}:
            raise ValueError("PM proposal decision must be approve or reject")
        proposals = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
        matching = self._find_pm_proposal(proposals, proposal_id, proposal_revision)
        allowed_statuses = {
            "approve": {"PENDING_APPROVAL", "APPROVED"},
            "reject": {"PENDING_APPROVAL", "REJECTED"},
        }
        if matching.get("status") not in allowed_statuses[clean_decision]:
            raise ValueError(f"PM proposal is already {matching.get('status')}")
        proposal = PMDecisionEnvelope.model_validate(matching.get("proposal", {}))
        action_name = f"{clean_decision}_pm_proposal"
        approval_summary = self._pm_approval_summary(proposal)
        descriptor = build_action_descriptor(
            project_name=project_name,
            action_name=action_name,
            target_type="pm_proposal",
            target_id=proposal_id,
            target_revision=proposal_revision,
            summary=approval_summary,
            source_state=proposal.source_state.model_dump(mode="json"),
            actor_boundary="product-director-human",
            idempotency_identity=(
                f"pm-proposal:{project_name}:{proposal_id}:{proposal_revision}:{clean_decision}"
            ),
            sealed_payload={
                "action_name": action_name,
                "project_name": project_name,
                "proposal_id": proposal_id,
                "proposal_revision": proposal_revision,
                "approval_summary": approval_summary,
                "source_state": proposal.source_state.model_dump(mode="json"),
                "proposal": proposal.model_dump(mode="json"),
            },
        )
        return descriptor.model_dump(mode="json")

    def render_pm_proposal_chat_fallback(
        self,
        project_name: str,
        proposal_id: str,
        proposal_revision: int,
    ) -> dict[str, Any]:
        """Return a safe, human-readable rendering of one exact sealed revision."""
        records = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
        record = self._find_pm_proposal(records, proposal_id, proposal_revision)
        decision = PMDecisionEnvelope.model_validate(record.get("proposal", {}))
        descriptor = self.describe_pm_proposal_decision(
            project_name,
            proposal_id,
            proposal_revision,
        )
        lines = [
            f"# AI Builder OS requirement proposal · revision {proposal_revision}",
            "",
            f"**Project:** {project_name}",
            f"**Proposal ID:** `{proposal_id}`",
            f"**Status:** {record.get('status', '')}",
            f"**Approval summary:** {descriptor['summary']}",
            "",
        ]
        if decision.facts:
            lines.extend(["## Facts", "", *[f"- {item}" for item in decision.facts], ""])
        if decision.assumptions:
            lines.extend(
                ["## Assumptions", "", *[f"- {item}" for item in decision.assumptions], ""]
            )
        lines.extend(["## Requirement changes", ""])
        for change in decision.requirement_changes:
            lines.extend(
                [
                    f"### {change.requirement_id} — {change.title}",
                    "",
                    f"- Action: {change.action}",
                    f"- Status: {change.status}",
                    f"- Priority: {change.priority}",
                    f"- Effort: {change.effort}",
                    f"- UI runtime: {change.ui_runtime or 'project default'}",
                    *(
                        [f"- Retirement reason: {change.retirement_reason}"]
                        if change.action == "retire"
                        else []
                    ),
                    "",
                    change.description,
                    "",
                ]
            )
        if decision.task_changes:
            lines.extend(["## Derived tasks", ""])
            for task in decision.task_changes:
                lines.extend(
                    [
                        f"### Task {task.task_number} — {task.title}",
                        "",
                        f"- Type: {task.task_type}",
                        f"- Requirement: {', '.join(task.requirement_ids)}",
                        f"- Goal: {task.goal}",
                        "- Required outcomes:",
                        *[f"  - {item}" for item in task.requirements],
                        "- Constraints:",
                        *[f"  - {item}" for item in task.constraints],
                        "- Validation:",
                        *[f"  - {item}" for item in task.validation],
                        "",
                    ]
                )
        requirement_label = (
            decision.requirement_changes[0].requirement_id
            if len(decision.requirement_changes) == 1
            else f"proposal {proposal_id}"
        )
        lines.extend(
            [
                "## Retained safety gates",
                "",
                "- Genuine missing product input",
                "- External or public actions, including release and deployment",
                "- API-billed Agents SDK execution",
                "- Destructive, privacy-sensitive, or secret-sensitive actions",
                "",
                "## Exact approval identity",
                "",
                f"- Proposal: `{proposal_id}`",
                f"- Revision: `{proposal_revision}`",
                f"- Seal: `{descriptor['sealed_payload_sha256']}`",
                "",
                f"To approve this exact displayed revision, reply: **Approve {requirement_label} revision {proposal_revision}**",
            ]
        )
        return {
            "project_name": project_name,
            "proposal_id": proposal_id,
            "proposal_revision": proposal_revision,
            "status": record.get("status", ""),
            "approval_summary": descriptor["summary"],
            "sealed_payload_sha256": descriptor["sealed_payload_sha256"],
            "markdown": "\n".join(lines).strip(),
        }

    def describe_pm_proposal_decision(
        self,
        project_name: str,
        proposal_id: str,
        proposal_revision: int,
    ) -> dict[str, Any]:
        proposals = load_json(control_data_dir(project_name) / "pm_proposals.json", [])
        matching = self._find_pm_proposal(proposals, proposal_id, proposal_revision)
        if matching.get("status") not in {
            "PENDING_APPROVAL",
            "APPROVED",
            "REJECTED",
        }:
            raise ValueError(f"PM proposal is already {matching.get('status')}")
        proposal = PMDecisionEnvelope.model_validate(matching.get("proposal", {}))
        approval_summary = self._pm_approval_summary(proposal)
        descriptor = build_action_descriptor(
            project_name=project_name,
            action_name="decide_pm_proposal",
            target_type="pm_proposal",
            target_id=proposal_id,
            target_revision=proposal_revision,
            summary=approval_summary,
            source_state=proposal.source_state.model_dump(mode="json"),
            actor_boundary="product-director-human",
            idempotency_identity=(
                f"pm-proposal:{project_name}:{proposal_id}:{proposal_revision}:decision"
            ),
            sealed_payload={
                "action_name": "decide_pm_proposal",
                "allowed_decisions": ["approve", "reject"],
                "project_name": project_name,
                "proposal_id": proposal_id,
                "proposal_revision": proposal_revision,
                "approval_summary": approval_summary,
                "source_state": proposal.source_state.model_dump(mode="json"),
                "proposal": proposal.model_dump(mode="json"),
            },
        )
        return descriptor.model_dump(mode="json")

    def decide_pm_proposal_from_native_prompt(
        self,
        project_name: str,
        proposal_id: str,
        proposal_revision: int,
        *,
        decision: str,
        expected_seal: str,
        actor: str,
        rejection_reason: str = "",
    ) -> dict[str, Any]:
        clean_decision = decision.strip().lower()
        descriptor = self.describe_pm_proposal_decision(
            project_name,
            proposal_id,
            proposal_revision,
        )
        if not expected_seal.strip() or expected_seal.strip() != descriptor["sealed_payload_sha256"]:
            raise ValueError("Native approval seal is stale or does not match the exact PM proposal action")
        clean_actor = actor.strip()
        if not clean_actor:
            raise ValueError("Native PM approval requires an explicit human actor label")
        if clean_decision == "approve":
            return self.approve_pm_proposal(
                project_name,
                proposal_id,
                proposal_revision,
                actor=clean_actor,
                source="codex-native-elicitation",
            )
        return self.reject_pm_proposal(
            project_name,
            proposal_id,
            proposal_revision,
            actor=clean_actor,
            source="codex-native-elicitation",
            reason=rejection_reason.strip() or "Rejected from the native Codex approval prompt.",
        )

    def record_native_external_approval_decision(
        self,
        project_name: str,
        *,
        approval_id: str,
        approval_type: str,
        decision: str,
        sealed_payload_sha256: str,
        actor: str,
    ) -> dict[str, Any]:
        clean_decision = decision.strip().lower()
        if clean_decision not in {"approve", "reject"}:
            raise ValueError("External approval decision must be approve or reject")
        if approval_type not in EXTERNAL_APPROVAL_RISKS:
            raise ValueError(f"Unknown external approval type: {approval_type}")
        if not sealed_payload_sha256.strip():
            raise ValueError("External approval decision requires an exact-action seal")
        clean_actor = actor.strip()
        if not clean_actor:
            raise ValueError("External approval decision requires an explicit human actor label")
        return append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "external_approval_decided",
                "actor": clean_actor,
                "source": "codex-native-elicitation",
                "approval_id": approval_id,
                "approval_type": approval_type,
                "decision": clean_decision,
                "sealed_payload_sha256": sealed_payload_sha256,
                "idempotency_key": (
                    f"native-external-approval:{project_name}:{approval_id}:{clean_decision}"
                ),
            },
        )

    def submit_pm_proposal(
        self,
        project_name: str,
        proposal: PMDecisionEnvelope | dict[str, Any],
        *,
        actor: str,
        source: str,
        idempotency_key: str = "",
        origin_request_id: str = "",
        origin_sdk_run_id: str = "",
    ) -> dict[str, Any]:
        decision = (
            PMDecisionEnvelope.model_validate(proposal.model_dump(mode="json"))
            if isinstance(proposal, PMDecisionEnvelope)
            else PMDecisionEnvelope.model_validate(proposal)
        )
        if decision.project_name and decision.project_name != project_name:
            raise ValueError("PM proposal project does not match the controller project")
        if not decision.assistant_message.strip():
            raise ValueError("PM proposal assistant_message must not be empty")
        if (
            decision.status == "READY_FOR_APPROVAL"
            and not decision.has_canonical_changes()
            and decision.mode not in {"artifact_review", "outcome_review"}
        ):
            raise ValueError("READY_FOR_APPROVAL proposals must contain canonical changes")
        if decision.status == "NEEDS_INPUT" and decision.has_canonical_changes():
            raise ValueError("NEEDS_INPUT proposals cannot contain canonical changes")

        origin_request: CodexWorkRequest | None = None
        origin_payload: PMWorkRequestPayload | None = None
        if origin_request_id.strip():
            origin_request = next(
                (
                    item
                    for item in self.list_codex_work_requests(project_name)
                    if item.request_id == origin_request_id.strip()
                ),
                None,
            )
            if origin_request is None:
                raise ValueError(f"Unknown originating Codex work request: {origin_request_id}")
            if origin_request.request_kind != "pm_decision" or origin_request.requested_role != "pm":
                raise ValueError("Originating work request is not a typed PM decision")
            if origin_request.status not in {"READY_FOR_CODEX", "CLAIMED_BY_CODEX"}:
                raise ValueError(f"Originating PM work request is already {origin_request.status}")
            origin_payload = PMWorkRequestPayload.model_validate(origin_request.payload)
            if decision.mode != origin_payload.mode:
                raise ValueError("PM proposal mode does not match its originating work request")
            if decision.work_request is not None and decision.work_request != origin_payload:
                raise ValueError("PM proposal work request does not match its origin")
            decision = decision.model_copy(update={"work_request": origin_payload})
            if origin_payload.parent_proposal_id:
                if decision.proposal_id and decision.proposal_id != origin_payload.parent_proposal_id:
                    raise ValueError("PM continuation must preserve its parent proposal ID")
                decision = decision.model_copy(
                    update={"proposal_id": origin_payload.parent_proposal_id}
                )
        elif decision.work_request is not None:
            origin_payload = decision.work_request
            if decision.mode != origin_payload.mode:
                raise ValueError("PM proposal mode does not match its typed work request")
            self._validate_pm_work_request(project_name, origin_payload)
            if origin_payload.parent_proposal_id:
                if decision.proposal_id and decision.proposal_id != origin_payload.parent_proposal_id:
                    raise ValueError("PM continuation must preserve its parent proposal ID")
                decision = decision.model_copy(
                    update={"proposal_id": origin_payload.parent_proposal_id}
                )
        elif origin_sdk_run_id.strip() and decision.mode in {
            "prioritisation",
            "task_plan",
            "artifact_review",
            "outcome_review",
        }:
            raise ValueError("Operational SDK PM proposals must echo their typed work request")

        automatic_task_plan = bool(
            decision.status == "READY_FOR_APPROVAL"
            and decision.mode == "task_plan"
            and origin_payload is not None
            and origin_payload.authorization_proposal_id
        )

        store_path = control_data_dir(project_name) / "pm_proposals.json"
        with project_lock(project_name):
            records = load_json(store_path, [])
            if idempotency_key:
                previous = next(
                    (item for item in records if item.get("idempotency_key") == idempotency_key),
                    None,
                )
                if previous:
                    return dict(previous)

            proposal_id = decision.proposal_id.strip() or str(uuid4())
            revisions = [
                int(item.get("proposal_revision", 0))
                for item in records
                if item.get("proposal_id") == proposal_id
            ]
            revision = max(revisions, default=0) + 1
            decision = self._materialize_pm_proposal_ids(
                project_name,
                decision.model_copy(
                    update={
                        "proposal_id": proposal_id,
                        "proposal_revision": revision,
                        "project_name": project_name,
                    }
                ),
            )
            current_source = self._pm_source_state(project_name)
            supplied = decision.source_state
            for field_name in ("requirements_sha256", "tasks_sha256", "memory_sha256"):
                expected = getattr(current_source, field_name)
                actual = getattr(supplied, field_name)
                if actual and actual != expected:
                    raise ValueError(f"PM proposal source state is stale: {field_name}")
            decision = decision.model_copy(update={"source_state": current_source})
            self._validate_pm_proposal(project_name, decision)
            if origin_payload is not None:
                self._validate_pm_proposal_against_work_request(decision, origin_payload)
            if automatic_task_plan:
                target_id = origin_payload.target_requirement_ids[0]
                self._validate_requirement_authorization(
                    project_name,
                    target_id,
                    origin_payload.authorization_proposal_id,
                    origin_payload.authorization_proposal_revision,
                )
                self._apply_pm_proposal(project_name, decision)

            for item in records:
                if (
                    item.get("proposal_id") == proposal_id
                    and item.get("status") in {"PENDING_APPROVAL", "NEEDS_INPUT"}
                ):
                    item["status"] = "SUPERSEDED"
                    item["resolved_at"] = utc_now()
                    item["resolved_by"] = actor.strip() or "unknown"
                    item["resolution_source"] = source.strip() or "unknown"

            record = PMProposalRecord(
                proposal_id=proposal_id,
                proposal_revision=revision,
                project_name=project_name,
                status=(
                    "AUTO_APPLIED"
                    if automatic_task_plan
                    else "PENDING_APPROVAL"
                    if decision.status == "READY_FOR_APPROVAL"
                    else "NEEDS_INPUT"
                ),
                actor=actor.strip() or "unknown",
                source=source.strip() or "unknown",
                submitted_at=utc_now(),
                proposal=decision.model_dump(mode="json"),
                idempotency_key=idempotency_key.strip(),
                origin_request_id=origin_request_id.strip(),
                parent_proposal_id=origin_payload.parent_proposal_id if origin_payload else "",
                parent_proposal_revision=origin_payload.parent_proposal_revision if origin_payload else 0,
                origin_sdk_run_id=origin_sdk_run_id.strip(),
            ).to_dict()
            records.append(record)
            atomic_write_json(store_path, records)

        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": (
                    "pm_derived_task_plan_auto_applied"
                    if automatic_task_plan
                    else "pm_proposal_submitted"
                ),
                "actor": record["actor"],
                "source": record["source"],
                "proposal_id": proposal_id,
                "proposal_revision": revision,
                "mode": decision.mode,
                "status": record["status"],
                "origin_request_id": record["origin_request_id"],
                "origin_sdk_run_id": record["origin_sdk_run_id"],
                "approval_summary": self._pm_approval_summary(decision),
                **self._pm_review_lineage(decision),
                "idempotency_key": f"pm-proposal:{idempotency_key}" if idempotency_key else "",
            },
        )
        if automatic_task_plan and origin_payload is not None:
            for index, intent in enumerate(decision.durable_intents):
                self.record_intent(
                    project_name,
                    intent,
                    actor=actor,
                    source=source,
                    idempotency_key=f"pm-auto:{proposal_id}:{revision}:intent:{index}",
                )
            assert origin_request is not None
            self.resolve_codex_work_request(
                project_name,
                origin_request.request_id,
                actor="deterministic-controller",
                status="COMPLETED",
                summary="Validated and auto-applied the task plan authorized by the approved requirement.",
                result_proposal_id=proposal_id,
                result_proposal_revision=revision,
            )
            self.ensure_autonomous_progress(
                project_name,
                requirement_id=origin_payload.target_requirement_ids[0],
                authorization_proposal_id=origin_payload.authorization_proposal_id,
                authorization_proposal_revision=origin_payload.authorization_proposal_revision,
            )
        return record

    def approve_pm_proposal(
        self,
        project_name: str,
        proposal_id: str,
        proposal_revision: int,
        *,
        actor: str,
        source: str,
    ) -> dict[str, Any]:
        store_path = control_data_dir(project_name) / "pm_proposals.json"
        durable_intents: list[str] = []
        retirement_events: list[dict[str, Any]] = []
        with project_lock(project_name):
            records = load_json(store_path, [])
            matching = self._find_pm_proposal(records, proposal_id, proposal_revision)
            if matching.get("status") == "APPROVED":
                return dict(matching)
            if matching.get("status") != "PENDING_APPROVAL":
                raise ValueError(f"PM proposal is already {matching.get('status')}")
            decision = PMDecisionEnvelope.model_validate(matching.get("proposal", {}))
            current_source = self._pm_source_state(project_name)
            if any(
                getattr(decision.source_state, field_name) != getattr(current_source, field_name)
                for field_name in (
                    "requirements_sha256",
                    "tasks_sha256",
                    "memory_sha256",
                    "history_event_id",
                )
            ):
                raise ValueError("PM proposal source state is stale; submit a refreshed revision")
            self._validate_pm_proposal(project_name, decision)
            retirement_events = self._apply_pm_proposal(
                project_name,
                decision,
                retirement_actor=actor.strip() or "unknown",
                retirement_authorization=f"pm-proposal:{proposal_id}:{proposal_revision}",
            )
            durable_intents = list(decision.durable_intents)
            matching["status"] = "APPROVED"
            matching["resolved_at"] = utc_now()
            matching["resolved_by"] = actor.strip() or "unknown"
            matching["resolution_source"] = source.strip() or "unknown"
            atomic_write_json(store_path, records)
            approved = dict(matching)

        for retirement in retirement_events:
            append_history(
                project_name,
                {
                    "event_id": str(uuid4()),
                    "event_type": "requirement_retired",
                    "actor": actor.strip() or "unknown",
                    "source": source.strip() or "unknown",
                    **retirement,
                    "idempotency_key": (
                        f"pm-proposal:{proposal_id}:{proposal_revision}:"
                        f"requirement-retired:{retirement['requirement_id']}"
                    ),
                },
            )
        for index, intent in enumerate(durable_intents):
            self.record_intent(
                project_name,
                intent,
                actor=actor,
                source=source,
                idempotency_key=f"pm-proposal:{proposal_id}:{proposal_revision}:intent:{index}",
            )
        approval_event = append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "pm_proposal_approved",
                "actor": actor.strip() or "unknown",
                "source": source.strip() or "unknown",
                "proposal_id": proposal_id,
                "proposal_revision": proposal_revision,
                "mode": decision.mode,
                "approval_summary": self._pm_approval_summary(decision),
                **self._pm_review_lineage(decision),
                "idempotency_key": f"pm-proposal:{proposal_id}:{proposal_revision}:approved",
            },
        )
        active_changes = [
            change
            for change in decision.requirement_changes
            if change.status == "IN_PROGRESS"
        ]
        if decision.mode == "requirement_draft" and len(active_changes) == 1:
            self.ensure_autonomous_progress(
                project_name,
                requirement_id=active_changes[0].requirement_id,
                authorization_proposal_id=proposal_id,
                authorization_proposal_revision=proposal_revision,
            )
        _refresh_codex_native_learning_observations(
            project_name, str(approval_event.get("event_id", proposal_id))
        )
        return approved

    def reject_pm_proposal(
        self,
        project_name: str,
        proposal_id: str,
        proposal_revision: int,
        *,
        actor: str,
        source: str,
        reason: str = "",
    ) -> dict[str, Any]:
        store_path = control_data_dir(project_name) / "pm_proposals.json"
        with project_lock(project_name):
            records = load_json(store_path, [])
            matching = self._find_pm_proposal(records, proposal_id, proposal_revision)
            if matching.get("status") == "REJECTED":
                return dict(matching)
            if matching.get("status") != "PENDING_APPROVAL":
                raise ValueError(f"PM proposal is already {matching.get('status')}")
            decision = PMDecisionEnvelope.model_validate(matching.get("proposal", {}))
            matching["status"] = "REJECTED"
            matching["resolved_at"] = utc_now()
            matching["resolved_by"] = actor.strip() or "unknown"
            matching["resolution_source"] = source.strip() or "unknown"
            matching["rejection_reason"] = " ".join(reason.split()).strip()
            atomic_write_json(store_path, records)
            rejected = dict(matching)
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "pm_proposal_rejected",
                "actor": actor.strip() or "unknown",
                "source": source.strip() or "unknown",
                "proposal_id": proposal_id,
                "proposal_revision": proposal_revision,
                "mode": decision.mode,
                **self._pm_review_lineage(decision),
                "reason": rejected["rejection_reason"],
                "idempotency_key": f"pm-proposal:{proposal_id}:{proposal_revision}:rejected",
            },
        )
        return rejected

    @staticmethod
    def _find_pm_proposal(
        records: list[dict[str, Any]],
        proposal_id: str,
        proposal_revision: int,
    ) -> dict[str, Any]:
        matching = next(
            (
                item
                for item in records
                if item.get("proposal_id") == proposal_id
                and int(item.get("proposal_revision", 0)) == proposal_revision
            ),
            None,
        )
        if matching is None:
            raise ValueError(f"Unknown PM proposal revision: {proposal_id}:{proposal_revision}")
        return matching

    def _pm_source_state(self, project_name: str) -> PMSourceState:
        root = project_path(project_name)
        memory_path = root / "memory.md"
        if not memory_path.exists():
            memory_path = root / "product" / "memory.md"
        history = [
            event
            for event in read_history(project_name, limit=1_000)
            if event.get("event_type") in self.PM_RELEVANT_HISTORY_EVENTS
        ]
        return PMSourceState(
            requirements_sha256=sha256_file(root / "product" / "requirements.md"),
            tasks_sha256=sha256_file(root / "product" / "tasks.md"),
            memory_sha256=sha256_file(memory_path),
            history_event_id=str(history[-1].get("event_id", "")) if history else "",
        )

    def _materialize_pm_proposal_ids(
        self,
        project_name: str,
        decision: PMDecisionEnvelope,
    ) -> PMDecisionEnvelope:
        from workspace import load_requirement_document, load_task_document

        requirement_document = load_requirement_document(project_name)
        existing_requirement_ids = {
            item.id for item in requirement_document.all_requirements
        }
        next_requirement_number = max(
            (int(item.removeprefix("R")) for item in existing_requirement_ids),
            default=0,
        ) + 1
        requirement_changes = []
        for change in decision.requirement_changes:
            if change.action == "create" and not change.requirement_id.strip():
                while f"R{next_requirement_number}" in existing_requirement_ids:
                    next_requirement_number += 1
                change = change.model_copy(update={"requirement_id": f"R{next_requirement_number}"})
                existing_requirement_ids.add(change.requirement_id)
                next_requirement_number += 1
            requirement_changes.append(change)

        task_document = load_task_document(project_name)
        task_numbers = {item.number for item in task_document.tasks}
        next_task_number = max(task_numbers, default=0) + 1
        task_changes = []
        for change in decision.task_changes:
            if change.action == "create" and change.task_number <= 0:
                while next_task_number in task_numbers:
                    next_task_number += 1
                change = change.model_copy(update={"task_number": next_task_number})
                task_numbers.add(next_task_number)
                next_task_number += 1
            task_changes.append(change)
        return decision.model_copy(
            update={
                "requirement_changes": requirement_changes,
                "task_changes": task_changes,
            }
        )

    def _validate_pm_proposal(
        self,
        project_name: str,
        decision: PMDecisionEnvelope,
        *,
        include_quality_guardrails: bool = True,
    ) -> None:
        from workspace import load_requirement_document, load_task_document

        if include_quality_guardrails:
            from pm_guardrails import collect_pm_guardrail_findings

            blocking = [
                item
                for item in collect_pm_guardrail_findings(project_name, decision)
                if item.severity == "blocking"
            ]
            if blocking:
                raise ValueError("; ".join(f"{item.code}: {item.message}" for item in blocking))

        if len(decision.assistant_message) > 12_000:
            raise ValueError("PM proposal assistant_message is too long")
        for item in decision.evidence:
            normalized = item.strip().casefold()
            if normalized.startswith(("external research:", "public web:")) and not re.search(
                r"https?://[^\s]+", item
            ):
                raise ValueError("External PM research evidence requires a source URL citation")
        if any(not value.strip() or len(value) > 4_000 for value in decision.durable_intents):
            raise ValueError("PM durable intents must be non-empty and 4000 characters or fewer")
        if decision.mode in {"artifact_review", "outcome_review"}:
            if decision.review_evidence is None:
                raise ValueError("PM review proposals require a deterministic evidence packet")
            review_target_id = (
                decision.artifact_review.artifact_id
                if decision.mode == "artifact_review"
                else decision.outcome_review.requirement_id
            )
            expected_evidence = self.build_pm_review_evidence(
                project_name,
                decision.mode,
                review_target_id,
            )
            if decision.review_evidence.model_dump(mode="json") != expected_evidence:
                raise ValueError(
                    "PM review evidence is stale or does not match the controller-built packet"
                )
        if decision.status == "NEEDS_INPUT":
            if decision.next_action not in {"ask_question", "request_clarification"}:
                raise ValueError("NEEDS_INPUT PM proposals must ask a question or request clarification")
            if decision.next_action == "request_clarification" and not decision.clarification.questions:
                raise ValueError("PM clarification requests must include at least one question")
            return

        expected_action = {
            "requirement_draft": "draft_requirement",
            "prioritisation": "prioritise_requirements",
            "task_plan": "plan_tasks",
            "artifact_review": "review_artifact",
            "outcome_review": "review_outcome",
        }
        if decision.mode in expected_action and decision.next_action != expected_action[decision.mode]:
            raise ValueError(f"PM mode {decision.mode} requires next_action {expected_action[decision.mode]}")
        if decision.mode == "requirement_draft" and not decision.requirement_changes:
            raise ValueError("Requirement draft proposals must include a requirement change")
        if decision.mode == "task_plan" and not decision.task_changes:
            raise ValueError("Task-plan proposals must include task changes")
        if decision.mode == "prioritisation" and not decision.prioritisation.selected_requirement_id:
            raise ValueError("Prioritisation proposals must select a requirement")
        requirement_document = load_requirement_document(project_name)
        requirements = {
            item.id: item for item in requirement_document.all_requirements
        }
        if decision.mode == "prioritisation":
            selected_id = decision.prioritisation.selected_requirement_id.strip()
            selected = requirements.get(selected_id)
            if selected is None or selected.status != "NEW":
                raise ValueError("Prioritisation must select an existing NEW requirement")
            deferred = decision.prioritisation.deferred_requirement_ids
            if (
                selected_id in deferred
                or len(deferred) != len(set(deferred))
                or any(item not in requirements or requirements[item].status != "NEW" for item in deferred)
            ):
                raise ValueError("Prioritisation must identify unique deferred NEW requirements")
            if not decision.prioritisation.rationale.strip() or not decision.prioritisation.evidence_basis.strip():
                raise ValueError("Prioritisation requires rationale and evidence basis")
            activation_changes = [
                item
                for item in decision.requirement_changes
                if item.action == "update"
                and item.requirement_id == selected_id
                and item.status == "IN_PROGRESS"
            ]
            if len(activation_changes) != 1 or len(decision.requirement_changes) != 1:
                raise ValueError("Prioritisation must activate exactly the selected requirement")
            if decision.task_changes:
                raise ValueError("Prioritisation proposals cannot also change tasks")

        if decision.mode == "task_plan":
            if decision.requirement_changes:
                raise ValueError("Task-plan proposals cannot also change requirements")
            linked_ids = {
                requirement_id
                for task in decision.task_changes
                for requirement_id in task.requirement_ids
            }
            if len(linked_ids) != 1:
                raise ValueError("Task planning must target exactly one requirement")
            target_id = next(iter(linked_ids))
            target = requirements.get(target_id)
            active_ids = [item.id for item in requirements.values() if item.status == "IN_PROGRESS"]
            if target is None or target.status != "IN_PROGRESS" or active_ids != [target_id]:
                raise ValueError("Task planning requires one IN_PROGRESS requirement")
            if any(set(task.requirement_ids) != {target_id} for task in decision.task_changes):
                raise ValueError("Every planned task must link only to the active requirement")
            if _requires_mockup_first(target):
                mockup_tasks = [task for task in decision.task_changes if _is_mockup_approval_task(task)]
                if not mockup_tasks:
                    raise ValueError(
                        "New user-facing projects and major UI features require a mockup-first Validation Task "
                        "with rendered route/state coverage, explicit Product Director approval, and a functionality-preservation map"
                    )
                first_task_number = min(task.task_number for task in decision.task_changes)
                if min(task.task_number for task in mockup_tasks) != first_task_number:
                    raise ValueError("The mockup approval Validation Task must be first in the task plan")

        if decision.mode == "artifact_review":
            artifact = decision.artifact_review
            assert decision.review_evidence is not None
            if decision.review_evidence.target_id != artifact.artifact_id:
                raise ValueError("Artifact review decision and evidence packet must target the same artifact")
            artifact_reference = next(
                (
                    item
                    for item in decision.review_evidence.references
                    if item.evidence_type == "artifact" and item.source_id == artifact.artifact_id
                ),
                None,
            )
            if artifact_reference is None or not artifact_reference.available or artifact_reference.status != "APPROVED":
                raise ValueError("Artifact review requires attributable approved-artifact evidence")
            from workspace import list_approvals

            source_artifact = next(
                (item for item in list_approvals(project_name) if item.approval_id == artifact.artifact_id),
                None,
            )
            if source_artifact is None or source_artifact.status != "APPROVED":
                raise ValueError("Artifact review source is not an approved workflow artifact")
            if not artifact.rationale.strip():
                raise ValueError("Artifact review requires rationale")
            if artifact.action == "merge":
                matching = [
                    item
                    for item in decision.requirement_changes
                    if item.action == "update" and item.requirement_id == artifact.target_requirement_id
                ]
                if not artifact.target_requirement_id.strip() or len(matching) != 1 or len(decision.requirement_changes) != 1:
                    raise ValueError("Artifact merge must update exactly its target requirement")
            elif artifact.action == "follow_up":
                if len(decision.requirement_changes) != 1 or decision.requirement_changes[0].action != "create":
                    raise ValueError("Artifact follow-up must propose exactly one new requirement")
            elif decision.requirement_changes or decision.task_changes:
                raise ValueError("Deferred or rejected artifacts cannot change requirements or tasks")

        if decision.mode == "outcome_review":
            outcome = decision.outcome_review
            assert decision.review_evidence is not None
            if decision.review_evidence.target_id != outcome.requirement_id:
                raise ValueError("Outcome review decision and evidence packet must target the same requirement")
            if outcome.requirement_id not in requirements:
                raise ValueError(f"Unknown outcome-review requirement: {outcome.requirement_id}")
            if not outcome.rationale.strip():
                raise ValueError("Outcome review requires rationale")
            if outcome.action in {"accept", "close"}:
                if decision.requirement_changes or decision.task_changes:
                    raise ValueError("Outcome acceptance cannot also mutate requirements or tasks")
                if outcome.follow_up_requirement_ids:
                    raise ValueError("Outcome closure cannot declare follow-up requirements")
                if (
                    outcome.action == "close"
                    and decision.review_evidence.missing_evidence
                    and not outcome.evidence_limitation.strip()
                ):
                    raise ValueError("Outcome closure with missing evidence requires an explicit limitation")
            elif outcome.action == "stop":
                if decision.requirement_changes or decision.task_changes or outcome.follow_up_requirement_ids:
                    raise ValueError("Stopping investment cannot create or modify follow-up work")
            elif not decision.has_canonical_changes():
                raise ValueError("Outcome follow-up decisions must propose bounded product work or durable intent")
            changed_ids = {
                item.requirement_id
                for item in decision.requirement_changes
            }
            if outcome.action in {"experiment", "revise"}:
                if (
                    not outcome.follow_up_requirement_ids
                    or set(outcome.follow_up_requirement_ids) != changed_ids
                ):
                    raise ValueError(
                        "Experiment and revise decisions must bind every changed follow-up requirement"
                    )
            elif changed_ids or outcome.follow_up_requirement_ids:
                if set(outcome.follow_up_requirement_ids) != changed_ids:
                    raise ValueError("Outcome follow-up lineage must match changed requirements")

            if outcome.follow_up_requirement_ids:
                from control_plane.storage import read_history

                for event in read_history(project_name, limit=500):
                    if (
                        event.get("event_type") != "pm_proposal_approved"
                        or event.get("review_target_id") != outcome.requirement_id
                        or event.get("review_action") != outcome.action
                    ):
                        continue
                    prior_ids = {
                        str(item)
                        for item in event.get("follow_up_requirement_ids", [])
                    }
                    if any(
                        item in requirements and requirements[item].status != "DONE"
                        for item in prior_ids
                    ):
                        raise ValueError(
                            "Equivalent outcome follow-up work is already open for this requirement"
                        )

        normalized_requirement_titles = {item.title.casefold(): item.id for item in requirements.values()}
        proposed_ids: set[str] = set()
        resulting_statuses = {item.id: item.status for item in requirements.values()}
        retirement_changes = [item for item in decision.requirement_changes if item.action == "retire"]
        if retirement_changes:
            if (
                decision.mode != "requirement_draft"
                or len(retirement_changes) != 1
                or len(decision.requirement_changes) != 1
                or decision.task_changes
            ):
                raise ValueError("Retirement must be one bounded requirement-draft change without task changes")
        for change in decision.requirement_changes:
            requirement_id = change.requirement_id.strip()
            if not requirement_id or not requirement_id.removeprefix("R").isdigit():
                raise ValueError("PM requirement changes require a valid R-number")
            if not change.title.strip() or not change.description.strip():
                raise ValueError("PM requirement changes require title and description")
            if change.action == "create":
                if requirement_id in requirements or requirement_id in proposed_ids:
                    raise ValueError(f"Duplicate PM requirement ID: {requirement_id}")
                duplicate = normalized_requirement_titles.get(change.title.strip().casefold())
                if duplicate:
                    raise ValueError(f"Duplicate PM requirement title matches {duplicate}")
                if change.status not in {"NEW", "BACKLOG", "IN_PROGRESS"}:
                    raise ValueError("New PM requirements require a valid initial status")
                proposed_ids.add(requirement_id)
            elif change.action == "update":
                existing = requirements.get(requirement_id)
                if existing is None:
                    raise ValueError(f"Unknown PM requirement update: {requirement_id}")
                if existing.status in {"DONE", "RETIRED"}:
                    raise ValueError(f"PM cannot update completed requirement: {requirement_id}")
                allowed_transitions = {
                    "NEW": {"NEW", "BACKLOG", "IN_PROGRESS"},
                    "BACKLOG": {"BACKLOG", "NEW", "IN_PROGRESS"},
                    "IN_PROGRESS": {"IN_PROGRESS"},
                }
                if change.status not in allowed_transitions.get(existing.status, {existing.status}):
                    raise ValueError(
                        f"Invalid PM requirement status transition: {existing.status} -> {change.status}"
                    )
            else:
                existing = requirements.get(requirement_id)
                if existing is None:
                    raise ValueError(f"Unknown PM requirement retirement: {requirement_id}")
                if existing.status not in {"NEW", "BACKLOG"}:
                    raise ValueError("Only NEW or BACKLOG requirements may be retired")
                unchanged_fields = (
                    change.title.strip() == existing.title.strip()
                    and change.priority == existing.priority
                    and change.effort == existing.effort
                    and change.description.strip() == existing.description.strip()
                    and change.ui_runtime.strip() == existing.ui_runtime.strip()
                )
                if not unchanged_fields:
                    raise ValueError("Retirement proposals must preserve the existing requirement content")
            resulting_statuses[requirement_id] = change.status
        if sum(status == "IN_PROGRESS" for status in resulting_statuses.values()) > 1:
            raise ValueError("PM proposals may leave only one requirement IN_PROGRESS")

        task_document = load_task_document(project_name)
        tasks = {item.number: item for item in task_document.tasks}
        task_titles = {item.title.casefold(): item.number for item in task_document.tasks}
        proposed_task_numbers: set[int] = set()
        known_requirement_ids = set(requirements) | proposed_ids
        for change in decision.task_changes:
            if change.task_number <= 0:
                raise ValueError("PM task changes require a positive task number")
            if not change.title.strip() or not change.goal.strip():
                raise ValueError("PM task changes require title and goal")
            if not change.requirement_ids or not set(change.requirement_ids).issubset(known_requirement_ids):
                raise ValueError("PM tasks must link only to known requirement IDs")
            if not change.requirements or not change.validation:
                raise ValueError("PM tasks require explicit requirements and validation")
            if change.action == "create":
                if change.task_number in tasks or change.task_number in proposed_task_numbers:
                    raise ValueError(f"Duplicate PM task number: {change.task_number}")
                duplicate_number = task_titles.get(change.title.strip().casefold())
                if duplicate_number:
                    raise ValueError(f"Duplicate PM task title matches Task {duplicate_number}")
                proposed_task_numbers.add(change.task_number)
            else:
                existing = tasks.get(change.task_number)
                if existing is None:
                    raise ValueError(f"Unknown PM task update: {change.task_number}")
                if existing.status != "TODO":
                    raise ValueError(f"PM cannot update task in status {existing.status}")

    @staticmethod
    def _validate_pm_proposal_against_work_request(
        decision: PMDecisionEnvelope,
        payload: PMWorkRequestPayload,
    ) -> None:
        if decision.status == "NEEDS_INPUT":
            if decision.mode == "artifact_review":
                if {decision.artifact_review.artifact_id} != set(payload.target_requirement_ids):
                    raise ValueError("Artifact-review proposal does not match its requested artifact")
            elif decision.mode == "outcome_review":
                if {decision.outcome_review.requirement_id} != set(payload.target_requirement_ids):
                    raise ValueError("Outcome-review proposal does not match its requested requirement")
            return
        targets = set(payload.target_requirement_ids)
        if decision.mode == "prioritisation":
            represented = {
                decision.prioritisation.selected_requirement_id,
                *decision.prioritisation.deferred_requirement_ids,
            }
            if represented != targets:
                raise ValueError("Prioritisation proposal does not cover its requested candidates")
        elif decision.mode == "task_plan":
            linked = {
                requirement_id
                for task in decision.task_changes
                for requirement_id in task.requirement_ids
            }
            if linked != targets:
                raise ValueError("Task-plan proposal does not match its requested requirement")
        elif decision.mode == "artifact_review":
            if {decision.artifact_review.artifact_id} != targets:
                raise ValueError("Artifact-review proposal does not match its requested artifact")
        elif decision.mode == "outcome_review":
            if {decision.outcome_review.requirement_id} != targets:
                raise ValueError("Outcome-review proposal does not match its requested requirement")

    def _apply_pm_proposal(
        self,
        project_name: str,
        decision: PMDecisionEnvelope,
        *,
        retirement_actor: str = "",
        retirement_authorization: str = "",
    ) -> list[dict[str, Any]]:
        from workspace import (
            RequirementRecord,
            TaskBlock,
            TaskDocument,
            load_requirement_document,
            load_task_document,
            save_requirement_document,
            save_task_document,
            retire_requirement,
        )

        root = project_path(project_name)
        requirements_path = root / "product" / "requirements.md"
        tasks_path = root / "product" / "tasks.md"
        runtime_decisions_path = root / "product" / "openai-runtime.json"
        original_requirements = requirements_path.read_text(encoding="utf-8")
        original_tasks = tasks_path.read_text(encoding="utf-8")
        original_runtime_decisions = (
            runtime_decisions_path.read_text(encoding="utf-8")
            if runtime_decisions_path.exists()
            else None
        )
        requirement_document = load_requirement_document(project_name)
        requirement_records = list(
            requirement_document.all_requirements
        )
        requirement_by_id = {item.id: index for index, item in enumerate(requirement_records)}
        retirement_changes = []
        for change in decision.requirement_changes:
            if change.action == "retire":
                retirement_changes.append(change)
                continue
            record = RequirementRecord(
                id=change.requirement_id,
                title=change.title.strip(),
                status=change.status,
                priority=change.priority,
                effort=change.effort,
                description=change.description.strip(),
                ui_runtime=change.ui_runtime.strip(),
            )
            if change.action == "create":
                requirement_records.append(record)
            else:
                requirement_records[requirement_by_id[change.requirement_id]] = record

        task_document = load_task_document(project_name)
        task_records = list(task_document.tasks)
        task_by_number = {item.number: index for index, item in enumerate(task_records)}
        for change in decision.task_changes:
            body_parts = ["Goal:", change.goal.strip()]
            for heading, values in (
                ("Requirements:", change.requirements),
                ("Constraints:", change.constraints),
                ("Validation:", change.validation),
            ):
                body_parts.extend(["", heading, *[f"- {value.strip()}" for value in values if value.strip()]])
            task = TaskBlock(
                number=change.task_number,
                title=change.title.strip(),
                task_type=change.task_type,
                status=change.status,
                requirements=tuple(change.requirement_ids),
                body="\n".join(body_parts).rstrip(),
            )
            if change.action == "create":
                task_records.append(task)
            else:
                task_records[task_by_number[change.task_number]] = task

        retirement_events: list[dict[str, Any]] = []
        try:
            if any(change.action != "retire" for change in decision.requirement_changes):
                save_requirement_document(project_name, requirement_records, requirement_document)
            if decision.task_changes:
                save_task_document(
                    project_name,
                    TaskDocument(intro=task_document.intro, tasks=tuple(task_records)),
                )
            for change in retirement_changes:
                if not retirement_actor.strip() or not retirement_authorization.strip():
                    raise ValueError("Approved retirement requires an actor and sealed authorization")
                retired_at = utc_now()
                result = retire_requirement(
                    project_name,
                    change.requirement_id,
                    reason=change.retirement_reason,
                    actor=retirement_actor,
                    retired_at=retired_at,
                    authorization=retirement_authorization,
                )
                retirement_events.append(
                    {
                        "requirement_id": change.requirement_id,
                        "reason": change.retirement_reason,
                        "retired_at": retired_at,
                        "authorization": retirement_authorization,
                        "retired_tasks": result.retired_tasks,
                        "updated_tasks": result.updated_tasks,
                        "preserved_done_tasks": result.preserved_done_tasks,
                    }
                )
        except Exception:
            atomic_write_text(requirements_path, original_requirements)
            atomic_write_text(tasks_path, original_tasks)
            if original_runtime_decisions is None:
                runtime_decisions_path.unlink(missing_ok=True)
            else:
                atomic_write_text(runtime_decisions_path, original_runtime_decisions)
            raise
        return retirement_events

    @staticmethod
    def _pm_approval_summary(decision: PMDecisionEnvelope) -> str:
        if decision.approval_summary.strip():
            return " ".join(decision.approval_summary.split()).strip()
        changes = [
            *[
                f"{item.action.title()} requirement {item.requirement_id}"
                for item in decision.requirement_changes
            ],
            *[
                f"{item.action.title()} Task {item.task_number}"
                for item in decision.task_changes
            ],
        ]
        if decision.durable_intents:
            changes.append(f"Record {len(decision.durable_intents)} durable intent item(s)")
        if decision.mode == "artifact_review":
            target = (
                f" into {decision.artifact_review.target_requirement_id}"
                if decision.artifact_review.target_requirement_id
                else ""
            )
            changes.append(
                f"{decision.artifact_review.action.replace('_', ' ').title()} "
                f"artifact {decision.artifact_review.artifact_id}{target}"
            )
        elif decision.mode == "outcome_review":
            changes.append(
                f"{decision.outcome_review.action.replace('_', ' ').title()} "
                f"outcome for {decision.outcome_review.requirement_id}"
            )
        return "; ".join(changes)

    @staticmethod
    def _pm_review_lineage(decision: PMDecisionEnvelope) -> dict[str, Any]:
        if decision.mode == "artifact_review":
            return {
                "review_target_id": decision.artifact_review.artifact_id,
                "review_action": decision.artifact_review.action,
            }
        if decision.mode == "outcome_review":
            return {
                "review_target_id": decision.outcome_review.requirement_id,
                "review_action": decision.outcome_review.action,
                "follow_up_requirement_ids": list(
                    decision.outcome_review.follow_up_requirement_ids
                ),
                "evidence_limitation": decision.outcome_review.evidence_limitation,
                "review_evidence_ids": (
                    [
                        f"{item.evidence_type}:{item.source_id}"
                        for item in decision.review_evidence.references
                    ]
                    if decision.review_evidence is not None
                    else []
                ),
                "review_missing_evidence": (
                    list(decision.review_evidence.missing_evidence)
                    if decision.review_evidence is not None
                    else []
                ),
            }
        return {}

    def claim_implementation(
        self,
        project_name: str,
        requirement_id: str,
        *,
        executor: str,
        idempotency_key: str = "",
        lease_minutes: int = 120,
    ) -> WorkPacket:
        from workspace import implementation_entry_allowed, load_requirement_document, load_task_document

        if lease_minutes < 5 or lease_minutes > 480:
            raise ValueError("lease_minutes must be between 5 and 480")
        document = load_requirement_document(project_name)
        record = next(
            (item for item in document.all_requirements if item.id == requirement_id),
            None,
        )
        if record is None:
            raise ValueError(f"Unknown requirement: {requirement_id}")
        if not implementation_entry_allowed(record):
            raise ValueError(f"{requirement_id} is not eligible for implementation")

        store_path = control_data_dir(project_name) / "interactive_runs.json"
        now = datetime.now(timezone.utc)
        with project_lock(project_name):
            runs = load_json(store_path, [])
            if idempotency_key:
                previous = next((item for item in runs if item.get("idempotency_key") == idempotency_key), None)
                if previous:
                    materialized = {
                        key: previous.get(key, () if key in {"tasks", "instructions"} else {})
                        for key in WorkPacket.__dataclass_fields__
                    }
                    materialized["tasks"] = tuple(materialized["tasks"])
                    materialized["instructions"] = tuple(materialized["instructions"])
                    return WorkPacket(**materialized)
            active = next(
                (
                    item
                    for item in runs
                    if item.get("project_name") == project_name
                    and item.get("requirement_id") == requirement_id
                    and item.get("status") == "CLAIMED"
                    and datetime.fromisoformat(item["expires_at"]) > now
                ),
                None,
            )
            if active:
                raise RuntimeError(f"{requirement_id} already has an active implementation lease")

            root = project_path(project_name)
            memory_path = root / "memory.md"
            if not memory_path.exists():
                memory_path = root / "product" / "memory.md"
            packet_instructions = [
                "Implement only the claimed requirement and preserve unrelated worktree changes.",
                "Continue through every task in this packet without requesting task-level product approval.",
                "Run proportionate specialist checks, tests, and QA, then record evidence before completing the run.",
                "Do not bypass approval gates for external or high-impact actions.",
            ]
            if _requires_mockup_first(record):
                packet_instructions.append(
                    "Apply the mockup-first product gate: complete and render the mockup across core routes/states and desktop/mobile layouts, "
                    "record a functionality-preservation map, and stop before application implementation until the Product Director explicitly approves the rendered mockup."
                )
            packet = WorkPacket(
                run_id=str(uuid4()),
                lease_token=secrets.token_urlsafe(32),
                project_name=project_name,
                requirement_id=requirement_id,
                executor=executor,
                status="CLAIMED",
                claimed_at=now.isoformat(),
                expires_at=(now + timedelta(minutes=lease_minutes)).isoformat(),
                requirement=asdict(record),
                tasks=tuple(
                    asdict(item)
                    for item in load_task_document(project_name).tasks
                    if record.id in item.requirements and item.status in {"TODO", "IN_PROGRESS"}
                ),
                product_files={
                    "requirements": str(root / "product" / "requirements.md"),
                    "tasks": str(root / "product" / "tasks.md"),
                    "memory": str(memory_path),
                    "history": str(root / "product" / "history.jsonl"),
                },
                instructions=tuple(packet_instructions),
            )
            payload = packet.to_dict() | {"idempotency_key": idempotency_key, "evidence": []}
            runs.append(payload)
            atomic_write_json(store_path, runs)
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "implementation_claimed",
                "actor": executor,
                "run_id": packet.run_id,
                "requirement_id": requirement_id,
            },
        )
        return packet

    def record_implementation_evidence(
        self,
        project_name: str,
        run_id: str,
        lease_token: str,
        *,
        summary: str,
        files_changed: list[str],
        tests: list[str],
        status: str = "COMPLETED",
        completed_task_numbers: list[int] | None = None,
        blocking_boundary: str = "",
        blocking_reason: str = "",
        retry_identity: str = "",
        retry_authorization_id: str = "",
        source_requirements_sha256: str = "",
        source_tasks_sha256: str = "",
    ) -> dict[str, Any]:
        if status not in {"COMPLETED", "FAILED", "BLOCKED"}:
            raise ValueError("status must be COMPLETED, FAILED, or BLOCKED")
        completed_numbers = list(completed_task_numbers or [])
        if (
            any(not isinstance(item, int) or item <= 0 for item in completed_numbers)
            or len(completed_numbers) != len(set(completed_numbers))
        ):
            raise ValueError("completed_task_numbers must contain unique positive task numbers")
        completed_numbers.sort()
        boundary = blocking_boundary.strip()
        if boundary not in self.BLOCKING_BOUNDARIES:
            raise ValueError(f"Unsupported blocking boundary: {boundary}")
        if status != "BLOCKED" and (boundary or blocking_reason.strip()):
            raise ValueError("Blocking details are valid only for BLOCKED evidence")
        if status == "BLOCKED" and boundary and not blocking_reason.strip():
            raise ValueError("Typed BLOCKED evidence requires a blocking reason")
        if completed_numbers and (
            not source_requirements_sha256.strip() or not source_tasks_sha256.strip()
        ):
            raise ValueError("Partial task reconciliation requires exact requirement and task source hashes")
        store_path = control_data_dir(project_name) / "interactive_runs.json"
        with project_lock(project_name):
            runs = load_json(store_path, [])
            run = next((item for item in runs if item.get("run_id") == run_id), None)
            if run is None or not secrets.compare_digest(str(run.get("lease_token", "")), lease_token):
                raise ValueError("Invalid run or lease token")
            if run.get("status") != "CLAIMED":
                raise ValueError(f"Run is already {run.get('status')}")
            requirement_id = str(run.get("requirement_id", ""))
            remaining_task_numbers = self._reconcile_partial_delivery(
                project_name,
                requirement_id,
                completed_numbers,
                complete_requirement=status == "COMPLETED",
                source_requirements_sha256=source_requirements_sha256,
                source_tasks_sha256=source_tasks_sha256,
            )
            run["status"] = status
            run["completed_at"] = utc_now()
            run["evidence"] = {
                "summary": summary.strip(),
                "files_changed": sorted(set(files_changed)),
                "tests": tests,
                "completed_task_numbers": completed_numbers,
                "remaining_task_numbers": remaining_task_numbers,
                "blocking_boundary": boundary,
                "blocking_reason": blocking_reason.strip(),
                "retry_identity": retry_identity.strip(),
                "retry_authorization_id": retry_authorization_id.strip(),
                "source_requirements_sha256": source_requirements_sha256.strip(),
                "source_tasks_sha256": source_tasks_sha256.strip(),
            }
            atomic_write_json(store_path, runs)
            public_run = {key: value for key, value in run.items() if key != "lease_token"}
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "implementation_evidence_recorded",
                "actor": run.get("executor", "unknown"),
                "run_id": run_id,
                "requirement_id": run.get("requirement_id", ""),
                "status": status,
                "summary": summary.strip(),
                "files_changed": sorted(set(files_changed)),
                "tests": tests,
                "completed_task_numbers": completed_numbers,
                "remaining_task_numbers": remaining_task_numbers,
                "blocking_boundary": boundary,
                "blocking_reason": blocking_reason.strip(),
                "retry_identity": retry_identity.strip(),
                "retry_authorization_id": retry_authorization_id.strip(),
            },
        )
        if completed_numbers:
            append_history(
                project_name,
                {
                    "event_id": str(uuid4()),
                    "event_type": "partial_delivery_reconciled",
                    "actor": "deterministic-controller",
                    "requirement_id": str(run.get("requirement_id", "")),
                    "run_id": run_id,
                    "completed_task_numbers": completed_numbers,
                    "remaining_task_numbers": remaining_task_numbers,
                    "idempotency_key": f"partial-delivery:{run_id}",
                },
            )
        if status == "COMPLETED" and not completed_numbers:
            self._reconcile_completed_delivery(
                project_name,
                str(run.get("requirement_id", "")),
                run_id=run_id,
            )
        return public_run

    def _reconcile_partial_delivery(
        self,
        project_name: str,
        requirement_id: str,
        completed_task_numbers: list[int],
        *,
        complete_requirement: bool,
        source_requirements_sha256: str,
        source_tasks_sha256: str,
    ) -> list[int]:
        from workspace import (
            RequirementRecord,
            TaskBlock,
            TaskDocument,
            load_requirement_document,
            load_task_document,
            save_requirement_document,
            save_task_document,
        )

        if not completed_task_numbers:
            try:
                task_document = load_task_document(project_name)
            except (FileNotFoundError, ValueError):
                return []
            return sorted(
                item.number
                for item in task_document.tasks
                if requirement_id in item.requirements and item.status in {"TODO", "IN_PROGRESS"}
            )
        requirement_document = load_requirement_document(project_name)
        task_document = load_task_document(project_name)
        linked = [item for item in task_document.tasks if requirement_id in item.requirements]
        root = project_path(project_name)
        if sha256_file(root / "product" / "requirements.md") != source_requirements_sha256:
            raise ValueError("Requirement source state changed before partial reconciliation")
        if sha256_file(root / "product" / "tasks.md") != source_tasks_sha256:
            raise ValueError("Task source state changed before partial reconciliation")
        records = list(
            requirement_document.all_requirements
        )
        target = next((item for item in records if item.id == requirement_id), None)
        if target is None or target.status != "IN_PROGRESS":
            raise ValueError("Partial reconciliation requires one active linked requirement")
        indexed = {item.number: item for item in linked}
        unknown = [item for item in completed_task_numbers if item not in indexed]
        if unknown:
            raise ValueError(
                f"Partial reconciliation contains unlinked tasks: {', '.join(str(item) for item in unknown)}"
            )
        ineligible = [
            item
            for item in completed_task_numbers
            if indexed[item].status not in {"TODO", "IN_PROGRESS"}
        ]
        if ineligible:
            raise ValueError(
                f"Partial reconciliation tasks are not pending: {', '.join(str(item) for item in ineligible)}"
            )
        updated_tasks: list[TaskBlock] = []
        for task in task_document.tasks:
            if task.number in completed_task_numbers:
                task = TaskBlock(
                    number=task.number,
                    title=task.title,
                    task_type=task.task_type,
                    status="DONE",
                    requirements=task.requirements,
                    body=task.body,
                )
            updated_tasks.append(task)
        remaining = sorted(
            task.number
            for task in updated_tasks
            if requirement_id in task.requirements and task.status in {"TODO", "IN_PROGRESS"}
        )
        save_task_document(
            project_name,
            TaskDocument(intro=task_document.intro, tasks=tuple(updated_tasks)),
        )
        if complete_requirement and not remaining:
            updated_records = [
                RequirementRecord(
                    id=item.id,
                    title=item.title,
                    status="DONE",
                    priority=item.priority,
                    effort=item.effort,
                    description=item.description,
                    ui_runtime=item.ui_runtime,
                )
                if item.id == requirement_id
                else item
                for item in records
            ]
            save_requirement_document(project_name, updated_records, requirement_document)
            self._supersede_orphaned_terminal_tasks(project_name)
        return remaining

    def _reconcile_completed_delivery(
        self,
        project_name: str,
        requirement_id: str,
        *,
        run_id: str,
    ) -> None:
        from workspace import (
            RequirementRecord,
            TaskBlock,
            TaskDocument,
            load_requirement_document,
            load_task_document,
            save_requirement_document,
            save_task_document,
        )

        try:
            requirement_document = load_requirement_document(project_name)
            task_document = load_task_document(project_name)
        except (FileNotFoundError, ValueError):
            return
        records = list(
            requirement_document.all_requirements
        )
        target = next((item for item in records if item.id == requirement_id), None)
        linked = [item for item in task_document.tasks if requirement_id in item.requirements]
        if target is None or target.status != "IN_PROGRESS" or not linked:
            return
        updated_tasks = []
        completed_numbers: list[int] = []
        for task in task_document.tasks:
            if requirement_id in task.requirements and task.status in {"TODO", "IN_PROGRESS"}:
                completed_numbers.append(task.number)
                task = TaskBlock(
                    number=task.number,
                    title=task.title,
                    task_type=task.task_type,
                    status="DONE",
                    requirements=task.requirements,
                    body=task.body,
                )
            updated_tasks.append(task)
        records = [
            RequirementRecord(
                id=item.id,
                title=item.title,
                status="DONE",
                priority=item.priority,
                effort=item.effort,
                description=item.description,
                ui_runtime=item.ui_runtime,
            )
            if item.id == requirement_id
            else item
            for item in records
        ]
        save_task_document(
            project_name,
            TaskDocument(intro=task_document.intro, tasks=tuple(updated_tasks)),
        )
        save_requirement_document(project_name, records, requirement_document)
        self._supersede_orphaned_terminal_tasks(project_name)
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "automatic_delivery_reconciled",
                "actor": "deterministic-controller",
                "requirement_id": requirement_id,
                "run_id": run_id,
                "completed_task_numbers": completed_numbers,
                "idempotency_key": f"automatic-delivery:{run_id}",
            },
        )

    def _supersede_orphaned_terminal_tasks(self, project_name: str) -> list[int]:
        from workspace import TaskBlock, TaskDocument, load_requirement_document, load_task_document, save_task_document

        requirements = load_requirement_document(project_name)
        statuses = {
            item.id: item.status
            for item in requirements.all_requirements
        }
        document = load_task_document(project_name)
        superseded: list[int] = []
        tasks = []
        for task in document.tasks:
            if (
                task.status in {"TODO", "IN_PROGRESS"}
                and task.requirements
                and all(statuses.get(item) == "DONE" for item in task.requirements)
            ):
                superseded.append(task.number)
                note = (
                    "\n\nLifecycle reconciliation:\n"
                    "Superseded because every linked requirement was already DONE; no completion evidence was inferred."
                )
                task = TaskBlock(
                    number=task.number,
                    title=task.title,
                    task_type=task.task_type,
                    status="SUPERSEDED",
                    requirements=task.requirements,
                    body=task.body.rstrip() + note,
                )
            tasks.append(task)
        if superseded:
            save_task_document(project_name, TaskDocument(intro=document.intro, tasks=tuple(tasks)))
        return superseded

    def history(self, project_name: str, *, limit: int = 50) -> list[dict[str, Any]]:
        return read_history(project_name, limit=limit)
