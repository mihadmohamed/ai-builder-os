from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from agents import RunConfig, RunState, Runner, SQLiteSession, gen_trace_id
from agents.models.interface import Model
from pydantic import BaseModel

from control_plane import WorkflowController
from control_plane.storage import append_history, atomic_write_json, control_data_dir, load_json, project_lock, utc_now

from .hooks import OSRunHooks
from .registry import DEFAULT_MODEL, build_agent_registry, build_structured_role_agent
from .support import AgentHandBackError, append_agent_trace, friendly_agent_runtime_error_message

AGENT_DEFINITION_VERSION = "2026-07-18-operational-pm-v2"
DISABLE_TRACING_ENV = "AI_BUILDER_OS_DISABLE_SDK_TRACING"


def _tracing_disabled() -> bool:
    return os.getenv(DISABLE_TRACING_ENV, "").strip().lower() in {"1", "true", "yes"}


class AgentsWorkflowRuntime:
    """Runs SDK agents with sessions, traces, and durable human approvals."""

    def __init__(self, *, model: str | Model = DEFAULT_MODEL) -> None:
        self.model = model

    def _registry(self):
        return build_agent_registry(self.model)

    def _model_label(self) -> str:
        if isinstance(self.model, str):
            return self.model
        return str(getattr(self.model, "model", type(self.model).__name__))

    def _context(
        self,
        project_name: str,
        *,
        actor: str,
        source: str,
        run_id: str = "",
        trace_id: str = "",
        role: str = "Orchestrator",
    ) -> dict[str, Any]:
        return {
            "project_name": project_name,
            "actor": actor,
            "source": source,
            "run_id": run_id,
            "trace_id": trace_id,
            "role": role,
            "active_role": role,
            "guardrail_findings": [],
        }

    def _session(self, project_name: str, session_id: str) -> SQLiteSession:
        path = control_data_dir(project_name) / "agent_sessions.sqlite3"
        return SQLiteSession(session_id, db_path=path)

    def run(
        self,
        project_name: str,
        prompt: str,
        *,
        agent_name: str = "orchestrator",
        actor: str = "user",
        source: str = "streamlit",
        session_id: str = "",
        max_turns: int = 10,
    ) -> dict[str, Any]:
        registry = self._registry()
        if agent_name not in registry:
            raise ValueError(f"Unknown agent: {agent_name}")
        run_id = str(uuid4())
        trace_id = gen_trace_id()
        session_id = session_id or f"{project_name}:{actor}"
        role = registry[agent_name].name
        context = self._context(
            project_name,
            actor=actor,
            source=source,
            run_id=run_id,
            trace_id=trace_id,
            role=role,
        )
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_started",
            role=role,
            model=self._model_label(),
            billing_backend="OpenAI API project",
        )
        session = self._session(project_name, session_id)
        try:
            result = Runner.run_sync(
                registry[agent_name],
                prompt,
                context=context,
                session=session,
                hooks=OSRunHooks(),
                max_turns=max_turns,
                run_config=RunConfig(
                    workflow_name="AI Builder OS deterministic workflow",
                    group_id=project_name,
                    trace_id=trace_id,
                    trace_metadata={"project_name": project_name, "source": source, "run_id": run_id},
                    tracing_disabled=_tracing_disabled(),
                    trace_include_sensitive_data=False,
                ),
            )
        except Exception as exc:
            self._record_run_event(project_name, trace_id, run_id, "run_failed", role=role, detail=str(exc))
            raise AgentHandBackError(friendly_agent_runtime_error_message(str(exc)), trace_id=trace_id) from exc
        finally:
            session.close()
        usage = self._usage_totals(result)
        payload = {
            "run_id": run_id,
            "session_id": session_id,
            "trace_id": trace_id,
            "execution_backend": "openai_agents_sdk",
            "billing": "OpenAI API project",
            "model": self._model_label(),
            "usage": usage,
            "status": "AWAITING_APPROVAL" if result.interruptions else "COMPLETED",
            "final_output": None if result.interruptions else self._serialize_output(result.final_output),
            "last_agent": result.last_agent.name,
            "approvals": [],
        }
        if result.interruptions:
            state_path = self._save_pending_state(
                project_name,
                run_id,
                agent_name,
                result.to_state().to_string(),
                actor=actor,
                source=source,
                session_id=session_id,
                trace_id=trace_id,
                interruptions=result.interruptions,
            )
            payload["state_path"] = str(state_path)
            payload["approvals"] = [self._approval_summary(run_id, index, item) for index, item in enumerate(result.interruptions)]
        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "sdk_agent_run_paused" if result.interruptions else "sdk_agent_run_completed",
                "actor": actor,
                "source": source,
                "run_id": run_id,
                "trace_id": trace_id,
                "initial_agent": agent_name,
                "last_agent": result.last_agent.name,
                "status": payload["status"],
            },
        )
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_paused" if result.interruptions else "run_completed",
            role=role,
            last_agent=result.last_agent.name,
            guardrails=context.get("guardrail_findings", []),
            **usage,
        )
        return payload

    def run_structured(
        self,
        project_name: str,
        *,
        role: str,
        instructions: str,
        input_messages: list[dict[str, Any]],
        output_type: type[BaseModel],
        model: str | Model | None = None,
        actor: str = "user",
        source: str = "streamlit",
        max_turns: int = 8,
    ) -> BaseModel:
        """Run one production role turn through the SDK-owned loop with structured output."""
        run_id = str(uuid4())
        trace_id = gen_trace_id()
        agent = build_structured_role_agent(
            role,
            instructions=instructions,
            output_type=output_type,
            model=model or self.model,
        )
        agent = agent.clone(
            tools=[
                tool
                for tool in agent.tools
                if not bool(getattr(tool, "needs_approval", False))
                and getattr(tool, "name", "") != "submit_pm_decision"
            ]
        )
        context = self._context(
            project_name,
            actor=actor,
            source=source,
            run_id=run_id,
            trace_id=trace_id,
            role=role,
        )
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_started",
            role=role,
            model=self._model_label(),
            billing_backend="OpenAI API project",
        )
        session = self._session(project_name, f"structured:{run_id}")
        try:
            result = Runner.run_sync(
                agent,
                input_messages,
                context=context,
                session=session,
                hooks=OSRunHooks(),
                max_turns=max_turns,
                run_config=RunConfig(
                    workflow_name=f"AI Builder OS {role} structured turn",
                    group_id=project_name,
                    trace_id=trace_id,
                    trace_metadata={"project_name": project_name, "source": source, "run_id": run_id, "role": role},
                    tracing_disabled=_tracing_disabled(),
                    trace_include_sensitive_data=False,
                ),
            )
        except Exception as exc:
            self._record_run_event(project_name, trace_id, run_id, "run_failed", role=role, detail=str(exc))
            raise AgentHandBackError(friendly_agent_runtime_error_message(str(exc)), trace_id=trace_id) from exc
        finally:
            session.close()
        if result.interruptions:
            self._record_run_event(project_name, trace_id, run_id, "run_failed", role=role, detail="unexpected approval interruption")
            raise AgentHandBackError("This structured role turn unexpectedly requested an approval.", trace_id=trace_id)
        if not isinstance(result.final_output, output_type):
            raise AgentHandBackError("The SDK agent did not return the required structured output.", trace_id=trace_id)
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_completed",
            role=role,
            last_agent=result.last_agent.name,
            guardrails=context.get("guardrail_findings", []),
            **self._usage_totals(result),
        )
        return result.final_output

    def resume(
        self,
        project_name: str,
        run_id: str,
        approval_id: str,
        *,
        approve: bool,
        actor: str,
        rejection_message: str = "",
    ) -> dict[str, Any]:
        pending_path = control_data_dir(project_name) / "pending_agent_runs.json"
        with project_lock(project_name):
            pending = load_json(pending_path, [])
            record = next((item for item in pending if item.get("run_id") == run_id), None)
            if record is not None and record.get("status") == "RESUMING":
                expires_at = str(record.get("resume_lease_expires_at", ""))
                try:
                    lease_expired = datetime.fromisoformat(expires_at) <= datetime.now(timezone.utc)
                except (TypeError, ValueError):
                    lease_expired = False
                if lease_expired:
                    record["status"] = "AWAITING_APPROVAL"
            if record is None or record.get("status") != "AWAITING_APPROVAL":
                raise ValueError(f"No pending SDK run: {run_id}")
            if record.get("agent_definition_version") != AGENT_DEFINITION_VERSION:
                raise ValueError("This pending SDK run uses an incompatible agent definition; start a new run")
            expected_prefix = f"{run_id}:"
            if not approval_id.startswith(expected_prefix):
                raise ValueError("Approval does not belong to this run")
            index = int(approval_id.removeprefix(expected_prefix))
            record["status"] = "RESUMING"
            record["resume_started_at"] = utc_now()
            record["resume_lease_expires_at"] = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
            atomic_write_json(pending_path, pending)
            record = dict(record)

        registry = self._registry()
        initial_agent = registry[str(record["initial_agent"])]
        context = self._context(
            project_name,
            actor=actor,
            source=str(record["source"]),
            run_id=run_id,
            trace_id=str(record["trace_id"]),
            role=initial_agent.name,
        )
        self._record_run_event(project_name, str(record["trace_id"]), run_id, "run_resuming", role=initial_agent.name)
        session = self._session(project_name, str(record["session_id"]))
        try:
            state = asyncio.run(
                RunState.from_string(initial_agent, str(record["state"]), context_override=context)
            )
            interruptions = state.get_interruptions()
            if index < 0 or index >= len(interruptions):
                raise ValueError("Unknown approval index")
            if approve:
                state.approve(interruptions[index])
            else:
                interruption = interruptions[index]
                if (interruption.tool_name or "") == "apply_pm_proposal":
                    raw = (
                        interruption.raw_item.model_dump(mode="json")
                        if hasattr(interruption.raw_item, "model_dump")
                        else interruption.raw_item
                    )
                    arguments = raw.get("arguments", "{}") if isinstance(raw, dict) else "{}"
                    parsed = json.loads(arguments) if isinstance(arguments, str) else dict(arguments)
                    WorkflowController().reject_pm_proposal(
                        project_name,
                        str(parsed.get("proposal_id", "")),
                        int(parsed.get("proposal_revision", 0)),
                        actor=actor,
                        source=str(record["source"]),
                        reason=rejection_message or "Rejected by user",
                    )
                state.reject(interruptions[index], rejection_message=rejection_message or "Rejected by user")
            result = Runner.run_sync(
                initial_agent,
                state,
                session=session,
                hooks=OSRunHooks(),
                run_config=RunConfig(
                    workflow_name="AI Builder OS deterministic workflow resume",
                    group_id=project_name,
                    trace_id=str(record["trace_id"]),
                    trace_metadata={"project_name": project_name, "source": record["source"], "run_id": run_id},
                    tracing_disabled=_tracing_disabled(),
                    trace_include_sensitive_data=False,
                ),
            )
        except Exception as exc:
            with project_lock(project_name):
                pending = load_json(pending_path, [])
                stored = next((item for item in pending if item.get("run_id") == run_id), None)
                if stored is not None and stored.get("status") == "RESUMING":
                    stored["status"] = "AWAITING_APPROVAL"
                    stored["resume_error"] = str(exc)
                    stored["updated_at"] = utc_now()
                    stored.pop("resume_lease_expires_at", None)
                    atomic_write_json(pending_path, pending)
            self._record_run_event(
                project_name,
                str(record["trace_id"]),
                run_id,
                "run_failed",
                role=initial_agent.name,
                detail=str(exc),
            )
            if isinstance(exc, ValueError):
                raise
            raise AgentHandBackError(
                friendly_agent_runtime_error_message(str(exc)), trace_id=str(record["trace_id"])
            ) from exc
        finally:
            session.close()

        with project_lock(project_name):
            pending = load_json(pending_path, [])
            stored = next((item for item in pending if item.get("run_id") == run_id), None)
            if stored is None or stored.get("status") != "RESUMING":
                raise ValueError("Pending SDK run changed while it was resuming")
            stored["state"] = result.to_state().to_string() if result.interruptions else ""
            stored["status"] = "AWAITING_APPROVAL" if result.interruptions else "COMPLETED"
            stored["resolved_by"] = actor
            stored["updated_at"] = utc_now()
            stored["approvals"] = [
                self._approval_summary(run_id, idx, item) for idx, item in enumerate(result.interruptions)
            ]
            stored.pop("resume_error", None)
            stored.pop("resume_lease_expires_at", None)
            atomic_write_json(pending_path, pending)
            record = dict(stored)

        append_history(
            project_name,
            {
                "event_id": str(uuid4()),
                "event_type": "sdk_agent_run_paused" if result.interruptions else "sdk_agent_run_completed",
                "actor": actor,
                "source": record["source"],
                "run_id": run_id,
                "trace_id": record["trace_id"],
                "last_agent": result.last_agent.name,
                "status": record["status"],
                "approval_id": approval_id,
                "approval_decision": "approved" if approve else "rejected",
            },
        )

        self._record_run_event(
            project_name,
            str(record["trace_id"]),
            run_id,
            "run_paused" if result.interruptions else "run_completed",
            role=initial_agent.name,
            last_agent=result.last_agent.name,
            approval_decision="approved" if approve else "rejected",
            guardrails=context.get("guardrail_findings", []),
            **self._usage_totals(result),
        )

        return {
            "run_id": run_id,
            "trace_id": record["trace_id"],
            "execution_backend": "openai_agents_sdk",
            "billing": "OpenAI API project",
            "model": self._model_label(),
            "usage": self._usage_totals(result),
            "status": record["status"],
            "final_output": None if result.interruptions else self._serialize_output(result.final_output),
            "last_agent": result.last_agent.name,
            "approvals": [self._approval_summary(run_id, idx, item) for idx, item in enumerate(result.interruptions)],
        }

    @staticmethod
    def _record_run_event(project_name: str, trace_id: str, run_id: str, event: str, **payload: Any) -> None:
        append_agent_trace(
            project_name,
            {
                "trace_id": trace_id,
                "run_id": run_id,
                "event": event,
                "runtime": "openai_agents_sdk",
                **payload,
            },
        )

    def _save_pending_state(
        self,
        project_name: str,
        run_id: str,
        initial_agent: str,
        state: str,
        *,
        actor: str,
        source: str,
        session_id: str,
        trace_id: str,
        interruptions: list[Any],
    ) -> Path:
        path = control_data_dir(project_name) / "pending_agent_runs.json"
        with project_lock(project_name):
            pending = load_json(path, [])
            pending.append(
                {
                    "run_id": run_id,
                    "project_name": project_name,
                    "initial_agent": initial_agent,
                    "state": state,
                    "status": "AWAITING_APPROVAL",
                    "actor": actor,
                    "source": source,
                    "session_id": session_id,
                    "trace_id": trace_id,
                    "agent_definition_version": AGENT_DEFINITION_VERSION,
                    "created_at": utc_now(),
                    "approvals": [self._approval_summary(run_id, index, item) for index, item in enumerate(interruptions)],
                }
            )
            atomic_write_json(path, pending)
        return path

    @staticmethod
    def _approval_summary(run_id: str, index: int, item: Any) -> dict[str, Any]:
        raw = item.raw_item.model_dump(mode="json") if hasattr(item.raw_item, "model_dump") else item.raw_item
        return {
            "approval_id": f"{run_id}:{index}",
            "tool_name": item.tool_name or "unknown",
            "arguments": raw.get("arguments", "") if isinstance(raw, dict) else "",
        }

    @staticmethod
    def _serialize_output(output: Any) -> Any:
        if isinstance(output, BaseModel):
            return output.model_dump(mode="json")
        if isinstance(output, (dict, list, str, int, float, bool)) or output is None:
            return output
        return str(output)

    @staticmethod
    def _usage_totals(result: Any) -> dict[str, int]:
        input_tokens = 0
        output_tokens = 0
        requests = 0
        for response in getattr(result, "raw_responses", []) or []:
            usage = getattr(response, "usage", None)
            input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
            output_tokens += int(getattr(usage, "output_tokens", 0) or 0)
            requests += int(getattr(usage, "requests", 0) or 0)
        return {"input_tokens": input_tokens, "output_tokens": output_tokens, "model_requests": requests}
