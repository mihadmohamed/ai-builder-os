from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
import os
import re
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from agents import ModelSettings, RunConfig, RunState, Runner, SQLiteSession, gen_trace_id
from agents.models.interface import Model
from openai.types.shared import Reasoning
from pydantic import BaseModel

from control_plane import WorkflowController
from control_plane.storage import append_history, atomic_write_json, control_data_dir, load_json, project_lock, utc_now
from pm_model_selection import sdk_pm_model_name, sdk_pm_reasoning_effort
from system_learning import record_from_trace_events, resolve_runtime_capability

from .hooks import OSRunHooks
from .registry import DEFAULT_MODEL, build_agent_registry, build_structured_role_agent
from .support import AgentHandBackError, append_agent_trace, friendly_agent_runtime_error_message, load_agent_traces

AGENT_DEFINITION_VERSION = "2026-08-23-capability-learning-v2"
DISABLE_TRACING_ENV = "AI_BUILDER_OS_DISABLE_SDK_TRACING"


def _tracing_disabled() -> bool:
    return os.getenv(DISABLE_TRACING_ENV, "").strip().lower() in {"1", "true", "yes"}


def _infer_pm_mode(prompt: str) -> str:
    match = re.search(
        r'\b(discovery|requirement_draft|prioritisation|task_plan|artifact_review|outcome_review)\b',
        prompt,
    )
    return match.group(1) if match else "discovery"


@dataclass(frozen=True)
class StructuredAgentRunResult:
    output: BaseModel
    run_id: str
    trace_id: str
    model: str
    usage: dict[str, int]
    latency_seconds: float
    tools: tuple[str, ...]
    guardrails: tuple[dict[str, Any], ...]


class AgentsWorkflowRuntime:
    """Runs SDK agents with sessions, traces, and durable human approvals."""

    def __init__(self, *, model: str | Model | None = None) -> None:
        self.model = model

    def _registry(self):
        return build_agent_registry(self.model)

    def _model_label(self, *, role: str = "") -> str:
        if isinstance(self.model, str):
            return self.model
        if self.model is None:
            return sdk_pm_model_name() if role == "PM" else DEFAULT_MODEL
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
        pm_mode: str = "",
    ) -> dict[str, Any]:
        return {
            "project_name": project_name,
            "actor": actor,
            "source": source,
            "run_id": run_id,
            "trace_id": trace_id,
            "role": role,
            "active_role": role,
            "pm_mode": pm_mode,
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
        pm_mode = _infer_pm_mode(prompt) if role == "PM" else ""
        capability = resolve_runtime_capability(role, pm_mode or "default")
        context = self._context(
            project_name,
            actor=actor,
            source=source,
            run_id=run_id,
            trace_id=trace_id,
            role=role,
            pm_mode=pm_mode,
        )
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_started",
            role=role,
            model=self._model_label(role=role),
            reasoning_effort=sdk_pm_reasoning_effort() if role == "PM" else "unavailable",
            workflow_mode=pm_mode or "default",
            capability_id=capability.capability_id,
            capability_version=capability.capability_version,
            change_marker=capability.change_marker,
            quality_eval_profile=capability.quality_eval_profile,
            billing_backend="OpenAI API project",
        )
        session = self._session(project_name, session_id)
        started_at = perf_counter()
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
            self._record_run_event(
                project_name, trace_id, run_id, "run_failed", role=role,
                detail=str(exc), latency_seconds=perf_counter() - started_at,
            )
            self._finalize_efficiency(project_name, trace_id, workflow_mode=pm_mode or "default")
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
            "model": self._model_label(role=role),
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
                pm_mode=pm_mode,
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
            latency_seconds=perf_counter() - started_at,
            **usage,
        )
        self._finalize_efficiency(project_name, trace_id, workflow_mode=pm_mode or "default")
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
        return self.run_structured_with_metadata(
            project_name,
            role=role,
            instructions=instructions,
            input_messages=input_messages,
            output_type=output_type,
            model=model,
            actor=actor,
            source=source,
            max_turns=max_turns,
        ).output

    def run_structured_with_metadata(
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
        pm_mode: str = "",
        reasoning_effort: str = "",
        max_output_tokens: int | None = None,
        evaluation_review_evidence: dict[str, Any] | None = None,
    ) -> StructuredAgentRunResult:
        """Run one isolated structured SDK turn and return privacy-safe execution telemetry."""
        run_id = str(uuid4())
        trace_id = gen_trace_id()
        agent = build_structured_role_agent(
            role,
            instructions=instructions,
            output_type=output_type,
            model=model if model is not None else self.model,
        )
        capability = resolve_runtime_capability(
            role, (pm_mode or "discovery") if role == "PM" else "default"
        )
        if reasoning_effort or max_output_tokens is not None:
            agent = agent.clone(
                model_settings=ModelSettings(
                    reasoning=Reasoning(effort=reasoning_effort) if reasoning_effort else None,
                    max_tokens=max_output_tokens,
                )
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
            pm_mode=(pm_mode or "discovery") if role == "PM" else "",
        )
        if evaluation_review_evidence is not None:
            if actor != "r101-evaluation" or not source.startswith("r101-sentinel:"):
                raise ValueError("Synthetic PM review evidence is restricted to the R101 evaluation runtime")
            context["evaluation_review_evidence"] = evaluation_review_evidence
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_started",
            role=role,
            model=(
                model
                if isinstance(model, str)
                else self._model_label(role=role)
            ),
            reasoning_effort=reasoning_effort or (sdk_pm_reasoning_effort() if role == "PM" else "unavailable"),
            workflow_mode=(pm_mode or "discovery") if role == "PM" else "default",
            capability_id=capability.capability_id,
            capability_version=capability.capability_version,
            change_marker=capability.change_marker,
            quality_eval_profile=capability.quality_eval_profile,
            billing_backend="OpenAI API project",
        )
        session = self._session(project_name, f"structured:{run_id}")
        started_at = perf_counter()
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
            self._record_run_event(
                project_name, trace_id, run_id, "run_failed", role=role,
                detail=str(exc), latency_seconds=perf_counter() - started_at,
            )
            self._finalize_efficiency(
                project_name, trace_id,
                workflow_mode=(pm_mode or "discovery") if role == "PM" else "default",
            )
            raise AgentHandBackError(friendly_agent_runtime_error_message(str(exc)), trace_id=trace_id) from exc
        finally:
            session.close()
        if result.interruptions:
            self._record_run_event(project_name, trace_id, run_id, "run_failed", role=role, detail="unexpected approval interruption")
            raise AgentHandBackError("This structured role turn unexpectedly requested an approval.", trace_id=trace_id)
        if not isinstance(result.final_output, output_type):
            raise AgentHandBackError("The SDK agent did not return the required structured output.", trace_id=trace_id)
        latency_seconds = perf_counter() - started_at
        usage = self._usage_totals(result)
        trace_events = [
            event
            for event in load_agent_traces(project_name)
            if str(event.get("trace_id", "")) == trace_id
        ]
        tools = tuple(
            str(event.get("tool", ""))
            for event in trace_events
            if event.get("event") == "tool_started" and event.get("tool")
        )
        self._record_run_event(
            project_name,
            trace_id,
            run_id,
            "run_completed",
            role=role,
            last_agent=result.last_agent.name,
            guardrails=context.get("guardrail_findings", []),
            latency_seconds=latency_seconds,
            **usage,
        )
        self._finalize_efficiency(
            project_name, trace_id,
            workflow_mode=(pm_mode or "discovery") if role == "PM" else "default",
        )
        return StructuredAgentRunResult(
            output=result.final_output,
            run_id=run_id,
            trace_id=trace_id,
            model=(
                model
                if isinstance(model, str)
                else self._model_label(role=role)
            ),
            usage=usage,
            latency_seconds=latency_seconds,
            tools=tools,
            guardrails=tuple(dict(item) for item in context.get("guardrail_findings", [])),
        )

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
            pm_mode=str(record.get("pm_mode", "")),
        )
        self._record_run_event(project_name, str(record["trace_id"]), run_id, "run_resuming", role=initial_agent.name)
        session = self._session(project_name, str(record["session_id"]))
        resumed_at = perf_counter()
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
            latency_seconds=perf_counter() - resumed_at,
            **self._usage_totals(result),
        )
        self._finalize_efficiency(
            project_name,
            str(record["trace_id"]),
            workflow_mode=str(record.get("pm_mode", "")) or "default",
        )

        return {
            "run_id": run_id,
            "trace_id": record["trace_id"],
            "execution_backend": "openai_agents_sdk",
            "billing": "OpenAI API project",
            "model": str(record.get("model", self._model_label(role=initial_agent.name))),
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

    @staticmethod
    def _finalize_efficiency(project_name: str, trace_id: str, *, workflow_mode: str) -> None:
        """Best-effort telemetry must never change the authoritative workflow outcome."""
        try:
            record_from_trace_events(project_name, trace_id, workflow_mode=workflow_mode)
        except Exception as exc:
            append_agent_trace(
                project_name,
                {
                    "trace_id": trace_id,
                    "event": "efficiency_telemetry_failed",
                    "runtime": "deterministic_system_learning",
                    "detail": str(exc)[:500],
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
        pm_mode: str,
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
                    "pm_mode": pm_mode,
                    "agent_definition_version": AGENT_DEFINITION_VERSION,
                    "model": self._model_label(role="PM" if initial_agent == "pm" else ""),
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
        cached_input_tokens = 0
        cache_write_tokens = 0
        output_tokens = 0
        reasoning_tokens = 0
        requests = 0
        for response in getattr(result, "raw_responses", []) or []:
            usage = getattr(response, "usage", None)
            input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
            input_details = getattr(usage, "input_tokens_details", None)
            cached_input_tokens += int(getattr(input_details, "cached_tokens", 0) or 0)
            cache_write_tokens += int(getattr(input_details, "cache_write_tokens", 0) or 0)
            output_tokens += int(getattr(usage, "output_tokens", 0) or 0)
            output_details = getattr(usage, "output_tokens_details", None)
            reasoning_tokens += int(getattr(output_details, "reasoning_tokens", 0) or 0)
            requests += int(getattr(usage, "requests", 0) or 0)
        return {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached_input_tokens,
            "cache_write_tokens": cache_write_tokens,
            "output_tokens": output_tokens,
            "reasoning_tokens": reasoning_tokens,
            "model_requests": requests,
        }
