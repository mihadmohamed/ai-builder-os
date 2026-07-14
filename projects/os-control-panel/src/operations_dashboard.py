from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from agents_runtime.support import TOOL_REGISTRY


AGENT_ROLE_MODES: dict[str, str] = {
    "PM": "Codex-native custom agent",
    "Experience Designer": "Codex-native custom agent",
    "UI Designer": "Codex-native custom agent",
    "Learning Agent": "Codex-native custom agent",
    "Architect": "Codex-native custom agent",
    "Orchestrator": "Codex-native controller + custom agent",
    "Engineer": "Codex-native implementation",
    "QA": "Codex-native custom agent",
}


@dataclass(frozen=True)
class AgentRunSummary:
    trace_id: str
    project_name: str
    role: str
    model: str
    status: str
    started_at: str
    finished_at: str
    duration_seconds: float | None
    attempts: int
    steps: int
    tools: tuple[str, ...]
    guardrail_count: int
    error_count: int
    hand_back_reason: str
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class AgentRolePerformance:
    role: str
    total_runs: int
    completed_runs: int
    hand_backs: int
    failed_runs: int
    completion_rate: int
    average_attempts: float
    average_steps: float
    tool_calls: int
    guardrail_findings: int
    execution_mode: str = "Observed agent"
    evidence_status: str = "Observed"


@dataclass(frozen=True)
class ToolUsageSummary:
    tool_name: str
    risk: str
    approval_required: bool
    read_only: bool
    calls: int
    roles: tuple[str, ...]
    projects: tuple[str, ...]
    denied_or_failed: int


def _parse_timestamp(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def _duration_seconds(started_at: str, finished_at: str) -> float | None:
    start = _parse_timestamp(started_at)
    finish = _parse_timestamp(finished_at)
    if start is None or finish is None:
        return None
    return max(0.0, round((finish - start).total_seconds(), 2))


def summarize_agent_runs(
    traces_by_project: dict[str, list[dict[str, object]]],
) -> list[AgentRunSummary]:
    grouped: dict[tuple[str, str], list[dict[str, object]]] = {}
    for project_name, events in traces_by_project.items():
        for event in events:
            trace_id = str(event.get("trace_id", "")).strip()
            if trace_id:
                grouped.setdefault((project_name, trace_id), []).append(event)

    summaries: list[AgentRunSummary] = []
    for (project_name, trace_id), events in grouped.items():
        ordered = sorted(events, key=lambda item: str(item.get("timestamp", "")))
        started = next((item for item in ordered if item.get("event") == "run_started"), ordered[0])
        completed = next((item for item in reversed(ordered) if item.get("event") == "run_completed"), None)
        hand_back = next((item for item in reversed(ordered) if item.get("event") in {"human_hand_back", "run_paused"}), None)
        errors = [item for item in ordered if item.get("event") in {"model_error", "run_failed"}]
        tool_events = [item for item in ordered if item.get("event") == "tool_completed"]
        terminal = completed or hand_back or (errors[-1] if errors else ordered[-1])
        status = "completed" if completed else "hand_back" if hand_back else "failed" if errors else "incomplete"
        tools = completed.get("tools", []) if completed else []
        if not isinstance(tools, list) or not tools:
            tools = [item.get("tool", "") for item in tool_events]
        guardrails = completed.get("guardrails", []) if completed else started.get("guardrails", [])
        if not isinstance(tools, list):
            tools = []
        if not isinstance(guardrails, list):
            guardrails = []
        attempts = int((completed or terminal).get("attempts", 0) or 0)
        if not attempts:
            attempts = max((int(item.get("attempt", 0) or 0) for item in ordered), default=0)
        steps = int((completed or terminal).get("steps", 0) or 0)
        if not steps:
            steps = max((int(item.get("step", 0) or 0) for item in ordered), default=0)
        started_at = str(started.get("timestamp", ""))
        finished_at = str(terminal.get("timestamp", ""))
        summaries.append(
            AgentRunSummary(
                trace_id=trace_id,
                project_name=project_name,
                role=str(started.get("role") or terminal.get("role") or "Unknown"),
                model=str(started.get("model", "")),
                status=status,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=_duration_seconds(started_at, finished_at),
                attempts=attempts,
                steps=steps,
                tools=tuple(str(item) for item in tools if str(item).strip()),
                guardrail_count=len(guardrails),
                error_count=len(errors),
                hand_back_reason=str((hand_back or {}).get("reason", "")),
                input_tokens=int((completed or {}).get("input_tokens", 0) or 0),
                output_tokens=int((completed or {}).get("output_tokens", 0) or 0),
                estimated_cost_usd=(
                    float(completed["estimated_cost_usd"])
                    if completed is not None and completed.get("estimated_cost_usd") is not None
                    else None
                ),
            )
        )
    return sorted(summaries, key=lambda item: item.started_at, reverse=True)


def summarize_role_performance(
    runs: Iterable[AgentRunSummary],
    *,
    role_modes: dict[str, str] | None = None,
) -> list[AgentRolePerformance]:
    configured_modes = role_modes or {}
    grouped: dict[str, list[AgentRunSummary]] = {role: [] for role in configured_modes}
    for run in runs:
        grouped.setdefault(run.role, []).append(run)
    output: list[AgentRolePerformance] = []
    for role, role_runs in grouped.items():
        total = len(role_runs)
        completed = sum(1 for run in role_runs if run.status == "completed")
        output.append(
            AgentRolePerformance(
                role=role,
                total_runs=total,
                completed_runs=completed,
                hand_backs=sum(1 for run in role_runs if run.status == "hand_back"),
                failed_runs=sum(1 for run in role_runs if run.status in {"failed", "incomplete"}),
                completion_rate=round(100 * completed / total) if total else 0,
                average_attempts=round(sum(run.attempts for run in role_runs) / total, 2) if total else 0.0,
                average_steps=round(sum(run.steps for run in role_runs) / total, 2) if total else 0.0,
                tool_calls=sum(len(run.tools) for run in role_runs),
                guardrail_findings=sum(run.guardrail_count for run in role_runs),
                execution_mode=configured_modes.get(role, "Observed agent"),
                evidence_status=(
                    "Live traces captured"
                    if total
                    else (
                        "No captured SDK runs"
                        if configured_modes.get(role) == "OpenAI Agents SDK"
                        else "Uses separate validation path"
                    )
                ),
            )
        )
    role_order = {role: index for index, role in enumerate(configured_modes)}
    return sorted(output, key=lambda item: (role_order.get(item.role, len(role_order)), item.role))


def summarize_tool_usage(
    traces_by_project: dict[str, list[dict[str, object]]],
) -> list[ToolUsageSummary]:
    calls: dict[str, list[tuple[str, str]]] = {name: [] for name in TOOL_REGISTRY}
    failures: dict[str, int] = {name: 0 for name in TOOL_REGISTRY}
    for project_name, events in traces_by_project.items():
        role_by_trace: dict[str, str] = {}
        for event in events:
            trace_id = str(event.get("trace_id", ""))
            role = str(event.get("role", "Unknown"))
            if trace_id and role != "Unknown":
                role_by_trace[trace_id] = role
            if event.get("event") == "tool_completed":
                tool = str(event.get("tool", ""))
                calls.setdefault(tool, []).append((role, project_name))
            if event.get("event") == "human_hand_back" and event.get("tool"):
                tool = str(event.get("tool", ""))
                failures[tool] = failures.get(tool, 0) + 1

    output: list[ToolUsageSummary] = []
    for name, definition in TOOL_REGISTRY.items():
        invocations = calls.get(name, [])
        output.append(
            ToolUsageSummary(
                tool_name=name,
                risk=definition.risk,
                approval_required=definition.approval_required,
                read_only=definition.read_only,
                calls=len(invocations),
                roles=tuple(sorted({role for role, _project in invocations})),
                projects=tuple(sorted({project for _role, project in invocations})),
                denied_or_failed=failures.get(name, 0),
            )
        )
    return sorted(output, key=lambda item: (-item.calls, item.tool_name))
