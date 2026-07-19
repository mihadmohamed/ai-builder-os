from __future__ import annotations

import secrets
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from pm_contract import PMDecisionEnvelope, PMSourceState, PMWorkRequestPayload
from tools.project_registry import list_project_locations, resolve_project

from .models import CodexWorkRequest, PMProposalRecord, WorkflowDecision, WorkPacket
from .storage import (
    append_history,
    atomic_write_json,
    atomic_write_text,
    control_data_dir,
    load_json,
    project_lock,
    project_path,
    read_history,
    sha256_file,
    utc_now,
)


class WorkflowController:
    """Single control plane used by Streamlit, MCP, workers, and SDK agents."""

    PM_RELEVANT_HISTORY_EVENTS = {
        "intent_recorded",
        "pm_proposal_approved",
        "pm_proposal_rejected",
        "implementation_evidence_recorded",
    }

    def list_projects(self) -> list[str]:
        return [item.name for item in list_project_locations()]

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
            "requirements": [asdict(item) for item in requirements.active_requirements + requirements.backlog_requirements],
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
        }
        if role not in allowed_roles:
            raise ValueError(f"Unsupported Codex role: {requested_role}")
        requirement_id = requirement_id.strip()
        request_kind = request_kind.strip() or "general"
        if request_kind not in {"general", "pm_decision"}:
            raise ValueError(f"Unsupported Codex work-request kind: {request_kind}")
        structured_payload = dict(payload or {})
        if request_kind == "general" and structured_payload:
            raise ValueError("General Codex work requests cannot contain a structured payload")
        if requirement_id:
            from workspace import load_requirement_document

            document = load_requirement_document(project_name)
            known_ids = {item.id for item in document.active_requirements + document.backlog_requirements}
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
        action = "prioritise" if request_payload.mode == "prioritisation" else "plan tasks for"
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
                if request_payload.mode == "task_plan"
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
        append_history(
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
            item.id: item for item in document.active_requirements + document.backlog_requirements
        }
        unknown = [item for item in payload.target_requirement_ids if item not in requirements]
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
        else:
            target = requirements[payload.target_requirement_ids[0]]
            active_ids = [item.id for item in requirements.values() if item.status == "IN_PROGRESS"]
            if target.status != "IN_PROGRESS" or active_ids != [target.id]:
                raise ValueError("Task planning requires one IN_PROGRESS requirement")

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
        from workspace import active_approvals, orchestrator_recommendation

        recommendation = orchestrator_recommendation(project_name)
        approvals = active_approvals(project_name)
        return WorkflowDecision(
            project_name=project_name,
            next_action=recommendation.next_action,
            next_role=recommendation.next_role,
            why=recommendation.why,
            blocking_approval_ids=tuple(item.approval_id for item in approvals),
        )

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
        if decision.status == "READY_FOR_APPROVAL" and not decision.has_canonical_changes():
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
        elif origin_sdk_run_id.strip() and decision.mode in {"prioritisation", "task_plan"}:
            raise ValueError("Operational SDK PM proposals must echo their typed work request")

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
                status="PENDING_APPROVAL" if decision.status == "READY_FOR_APPROVAL" else "NEEDS_INPUT",
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
                "event_type": "pm_proposal_submitted",
                "actor": record["actor"],
                "source": record["source"],
                "proposal_id": proposal_id,
                "proposal_revision": revision,
                "mode": decision.mode,
                "status": record["status"],
                "origin_request_id": record["origin_request_id"],
                "origin_sdk_run_id": record["origin_sdk_run_id"],
                "approval_summary": self._pm_approval_summary(decision),
                "idempotency_key": f"pm-proposal:{idempotency_key}" if idempotency_key else "",
            },
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
            self._apply_pm_proposal(project_name, decision)
            durable_intents = list(decision.durable_intents)
            matching["status"] = "APPROVED"
            matching["resolved_at"] = utc_now()
            matching["resolved_by"] = actor.strip() or "unknown"
            matching["resolution_source"] = source.strip() or "unknown"
            atomic_write_json(store_path, records)
            approved = dict(matching)

        for index, intent in enumerate(durable_intents):
            self.record_intent(
                project_name,
                intent,
                actor=actor,
                source=source,
                idempotency_key=f"pm-proposal:{proposal_id}:{proposal_revision}:intent:{index}",
            )
        append_history(
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
                "idempotency_key": f"pm-proposal:{proposal_id}:{proposal_revision}:approved",
            },
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
            item.id for item in requirement_document.active_requirements + requirement_document.backlog_requirements
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

    def _validate_pm_proposal(self, project_name: str, decision: PMDecisionEnvelope) -> None:
        from workspace import load_requirement_document, load_task_document

        if len(decision.assistant_message) > 12_000:
            raise ValueError("PM proposal assistant_message is too long")
        if any(not value.strip() or len(value) > 4_000 for value in decision.durable_intents):
            raise ValueError("PM durable intents must be non-empty and 4000 characters or fewer")
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
            item.id: item for item in requirement_document.active_requirements + requirement_document.backlog_requirements
        }
        if decision.mode == "prioritisation":
            selected_id = decision.prioritisation.selected_requirement_id.strip()
            selected = requirements.get(selected_id)
            if selected is None or selected.status != "NEW":
                raise ValueError("Prioritisation must select an existing NEW requirement")
            deferred = decision.prioritisation.deferred_requirement_ids
            if (
                not deferred
                or selected_id in deferred
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

        normalized_requirement_titles = {item.title.casefold(): item.id for item in requirements.values()}
        proposed_ids: set[str] = set()
        resulting_statuses = {item.id: item.status for item in requirements.values()}
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
                if change.status not in {"NEW", "BACKLOG"}:
                    raise ValueError("New PM requirements must start as NEW or BACKLOG")
                proposed_ids.add(requirement_id)
            else:
                existing = requirements.get(requirement_id)
                if existing is None:
                    raise ValueError(f"Unknown PM requirement update: {requirement_id}")
                if existing.status == "DONE":
                    raise ValueError(f"PM cannot update completed requirement: {requirement_id}")
                allowed_transitions = {
                    "NEW": {"NEW", "BACKLOG", "IN_PROGRESS"},
                    "BACKLOG": {"BACKLOG", "NEW"},
                    "IN_PROGRESS": {"IN_PROGRESS"},
                }
                if change.status not in allowed_transitions.get(existing.status, {existing.status}):
                    raise ValueError(
                        f"Invalid PM requirement status transition: {existing.status} -> {change.status}"
                    )
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
            return
        targets = set(payload.target_requirement_ids)
        if decision.mode == "prioritisation":
            represented = {
                decision.prioritisation.selected_requirement_id,
                *decision.prioritisation.deferred_requirement_ids,
            }
            if represented != targets:
                raise ValueError("Prioritisation proposal does not cover its requested candidates")
        elif decision.status == "READY_FOR_APPROVAL":
            linked = {
                requirement_id
                for task in decision.task_changes
                for requirement_id in task.requirement_ids
            }
            if linked != targets:
                raise ValueError("Task-plan proposal does not match its requested requirement")

    def _apply_pm_proposal(self, project_name: str, decision: PMDecisionEnvelope) -> None:
        from workspace import (
            RequirementRecord,
            TaskBlock,
            TaskDocument,
            load_requirement_document,
            load_task_document,
            save_requirement_document,
            save_task_document,
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
            requirement_document.active_requirements + requirement_document.backlog_requirements
        )
        requirement_by_id = {item.id: index for index, item in enumerate(requirement_records)}
        for change in decision.requirement_changes:
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

        try:
            if decision.requirement_changes:
                save_requirement_document(project_name, requirement_records, requirement_document)
            if decision.task_changes:
                save_task_document(
                    project_name,
                    TaskDocument(intro=task_document.intro, tasks=tuple(task_records)),
                )
        except Exception:
            atomic_write_text(requirements_path, original_requirements)
            atomic_write_text(tasks_path, original_tasks)
            if original_runtime_decisions is None:
                runtime_decisions_path.unlink(missing_ok=True)
            else:
                atomic_write_text(runtime_decisions_path, original_runtime_decisions)
            raise

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
        return "; ".join(changes)

    def claim_implementation(
        self,
        project_name: str,
        requirement_id: str,
        *,
        executor: str,
        idempotency_key: str = "",
        lease_minutes: int = 120,
    ) -> WorkPacket:
        from workspace import implementation_entry_allowed, load_requirement_document

        if lease_minutes < 5 or lease_minutes > 480:
            raise ValueError("lease_minutes must be between 5 and 480")
        document = load_requirement_document(project_name)
        record = next(
            (item for item in document.active_requirements + document.backlog_requirements if item.id == requirement_id),
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
                    return WorkPacket(**{key: previous[key] for key in WorkPacket.__dataclass_fields__})
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
                product_files={
                    "requirements": str(root / "product" / "requirements.md"),
                    "tasks": str(root / "product" / "tasks.md"),
                    "memory": str(memory_path),
                    "history": str(root / "product" / "history.jsonl"),
                },
                instructions=(
                    "Implement only the claimed requirement and preserve unrelated worktree changes.",
                    "Run proportionate tests and record evidence before completing the run.",
                    "Do not bypass approval gates for external or high-impact actions.",
                ),
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
    ) -> dict[str, Any]:
        if status not in {"COMPLETED", "FAILED", "BLOCKED"}:
            raise ValueError("status must be COMPLETED, FAILED, or BLOCKED")
        store_path = control_data_dir(project_name) / "interactive_runs.json"
        with project_lock(project_name):
            runs = load_json(store_path, [])
            run = next((item for item in runs if item.get("run_id") == run_id), None)
            if run is None or not secrets.compare_digest(str(run.get("lease_token", "")), lease_token):
                raise ValueError("Invalid run or lease token")
            if run.get("status") != "CLAIMED":
                raise ValueError(f"Run is already {run.get('status')}")
            run["status"] = status
            run["completed_at"] = utc_now()
            run["evidence"] = {
                "summary": summary.strip(),
                "files_changed": sorted(set(files_changed)),
                "tests": tests,
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
            },
        )
        return public_run

    def history(self, project_name: str, *, limit: int = 50) -> list[dict[str, Any]]:
        return read_history(project_name, limit=limit)
