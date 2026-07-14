from __future__ import annotations

import secrets
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from tools.project_registry import list_project_locations, resolve_project

from .models import CodexWorkRequest, WorkflowDecision, WorkPacket
from .storage import (
    append_history,
    atomic_write_json,
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

    def list_projects(self) -> list[str]:
        return [item.name for item in list_project_locations()]

    def snapshot(self, project_name: str) -> dict[str, Any]:
        from workspace import active_approvals, list_implementation_runs, load_requirement_document, load_task_document

        location = resolve_project(project_name)
        root = location.workspace_path
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
            "canonical_hashes": {
                "requirements": sha256_file(root / "product" / "requirements.md"),
                "tasks": sha256_file(root / "product" / "tasks.md"),
                "memory": sha256_file(root / "product" / "memory.md"),
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
                "idempotency_key": f"codex-work:{idempotency_key}" if idempotency_key else "",
            },
        )
        return request

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
            matching["status"] = terminal_status
            matching["resolved_at"] = utc_now()
            matching["summary"] = clean_summary
            matching["implementation_run_id"] = implementation_run_id.strip()
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
            },
        )
        return request

    @staticmethod
    def _codex_work_request_from_dict(payload: dict[str, Any]) -> CodexWorkRequest:
        return CodexWorkRequest(
            **{key: str(payload.get(key, "")) for key in CodexWorkRequest.__dataclass_fields__}
        )

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
                    "memory": str(root / "product" / "memory.md"),
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
