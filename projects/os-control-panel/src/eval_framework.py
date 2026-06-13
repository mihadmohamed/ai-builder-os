from __future__ import annotations

import ast
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable


EVAL_TYPE_DESCRIPTIONS: dict[str, str] = {
    "Output Quality": "Checks that an agent response contains the required, grounded, useful result.",
    "Tool Selection": "Checks whether the agent chose the required tools without unsafe or unnecessary calls.",
    "Workflow": "Checks that multi-step routing and state transitions reach the expected outcome.",
    "Memory": "Checks that required remembered facts are used and stale or forbidden facts are excluded.",
    "Safety": "Checks guardrails, authorization boundaries, redaction, and human hand-back behavior.",
    "Cost": "Checks measured token usage and estimated model spend against an explicit run budget.",
    "Latency": "Checks measured end-to-end duration against an explicit response-time budget.",
    "Reliability": "Checks completion rate, terminal trace integrity, and repeat-run consistency.",
}


@dataclass(frozen=True)
class EvalResult:
    eval_type: str
    passed: bool
    score: int
    summary: str
    failures: tuple[str, ...] = ()


@dataclass(frozen=True)
class EvalCoverageRecord:
    project_name: str
    agents: str
    eval_type: str
    implementation: str


@dataclass(frozen=True)
class EvalCaseRecord:
    case_id: str
    title: str
    project_name: str
    agents: str
    eval_type: str
    description: str
    expected_summary: str
    source_path: str
    payload_json: str


EVAL_COVERAGE: tuple[EvalCoverageRecord, ...] = (
    EvalCoverageRecord("os-control-panel", "Learning Agent", "Output Quality", "Tutoring grounding, clarification, explanation-back, and progression scenarios."),
    EvalCoverageRecord("parentmate", "Email Extraction Agent", "Output Quality", "Replay and live structured-output comparisons against expected email data."),
    EvalCoverageRecord("career-guidance", "Career Advisor", "Output Quality", "Expected skill gaps and development-plan completeness."),
    EvalCoverageRecord("dream-translator", "Dream Analysis Agent", "Output Quality", "Expected readiness, themes, insights, and prompt content."),
    EvalCoverageRecord("os-control-panel", "PM, Experience Designer, UI Designer, Learning Agent, Orchestrator", "Tool Selection", "Expected, missing, unnecessary, ordered, unauthorized, and failed tool-call grading."),
    EvalCoverageRecord("os-control-panel", "PM, Experience Designer, Architect, Orchestrator, Learning Agent", "Workflow", "Deterministic routing, handoff, cleanup, locking, tutoring, and progression scenarios."),
    EvalCoverageRecord("Trip planner", "Trip Planning Agent", "Workflow", "Planning, filtering, feedback persistence, and selection behavior."),
    EvalCoverageRecord("os-control-panel", "Learning Agent and all memory-capable live roles", "Memory", "Required-fact recall, stale-fact rejection, persistence, and memory-tool-use grading."),
    EvalCoverageRecord("os-control-panel", "All bounded live agents", "Safety", "Injection, authorization, redaction, unsupported-action, limits, and hand-back checks."),
    EvalCoverageRecord("os-control-panel", "All bounded live agents", "Cost", "Captured input/output tokens and estimated per-run spend checked against budgets."),
    EvalCoverageRecord("os-control-panel", "All bounded live agents", "Latency", "Captured model and end-to-end duration checked against role-independent budgets."),
    EvalCoverageRecord("All evaluated projects", "All evaluated agents/components", "Reliability", "Terminal trace integrity, regression suites, repeated outcomes, and completion-rate thresholds."),
)


def load_eval_case_catalog(repo_root: Path) -> tuple[EvalCaseRecord, ...]:
    cases: list[EvalCaseRecord] = []
    cases.extend(_load_os_capability_cases(repo_root))
    cases.extend(_load_os_scenarios(repo_root))
    cases.extend(_load_parentmate_cases(repo_root))
    cases.extend(_load_json_fixture_cases(repo_root))
    cases.extend(_load_trip_planner_cases(repo_root))
    return tuple(sorted(cases, key=lambda item: (item.project_name.lower(), item.eval_type, item.case_id)))


def _payload_json(payload: object) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


def _relative_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo_root))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_os_capability_cases(repo_root: Path) -> list[EvalCaseRecord]:
    path = repo_root / "projects" / "os-control-panel" / "evals" / "eval_cases.json"
    raw_cases = _load_json(path)
    if not isinstance(raw_cases, list):
        return []
    records: list[EvalCaseRecord] = []
    for raw in raw_cases:
        if not isinstance(raw, dict):
            continue
        eval_type = str(raw.get("eval_type", "Reliability"))
        case_id = str(raw.get("id", "unnamed"))
        expected_keys = {
            key: value
            for key, value in raw.items()
            if key.startswith(("expected", "required", "forbidden", "max_", "minimum_", "order_"))
        }
        records.append(
            EvalCaseRecord(
                case_id=case_id,
                title=case_id.replace("_", " ").title(),
                project_name="os-control-panel",
                agents=_agents_for_eval_type(eval_type),
                eval_type=eval_type,
                description=EVAL_TYPE_DESCRIPTIONS.get(eval_type, "Executable evaluation contract."),
                expected_summary=_payload_json(expected_keys) if expected_keys else "The configured contract must pass.",
                source_path=_relative_path(repo_root, path),
                payload_json=_payload_json(raw),
            )
        )
    return records


def _scenario_eval_type(case_id: str) -> str:
    if case_id == "tutoring_recommendations_compound_after_progress":
        return "Memory"
    if case_id.startswith("tutoring_") and case_id not in {
        "tutoring_progression_and_build_routing_are_sensible",
    }:
        return "Output Quality"
    return "Workflow"


def _load_os_scenarios(repo_root: Path) -> list[EvalCaseRecord]:
    path = repo_root / "projects" / "os-control-panel" / "evals" / "scenarios.json"
    raw_cases = _load_json(path)
    if not isinstance(raw_cases, list):
        return []
    records: list[EvalCaseRecord] = []
    for raw in raw_cases:
        if not isinstance(raw, dict):
            continue
        case_id = str(raw.get("id", "unnamed"))
        eval_type = _scenario_eval_type(case_id)
        records.append(
            EvalCaseRecord(
                case_id=case_id,
                title=str(raw.get("title", case_id.replace("_", " ").title())),
                project_name="os-control-panel",
                agents="Learning Agent" if case_id.startswith("tutoring_") else "PM, Experience Designer, Architect, Orchestrator",
                eval_type=eval_type,
                description=str(raw.get("description", "Deterministic workflow scenario.")),
                expected_summary=_payload_json(raw.get("expected", {})),
                source_path=_relative_path(repo_root, path),
                payload_json=_payload_json(raw),
            )
        )
    return records


def _load_parentmate_cases(repo_root: Path) -> list[EvalCaseRecord]:
    evals_dir = repo_root / "projects" / "parentmate" / "evals"
    records: list[EvalCaseRecord] = []
    for input_path in sorted(evals_dir.glob("email_*.txt")):
        expected_path = input_path.with_name(f"{input_path.stem}_expected.json")
        replay_path = evals_dir / "replays" / f"{input_path.stem}_response.json"
        expected = _load_json(expected_path)
        payload = {
            "input": input_path.read_text(encoding="utf-8", errors="replace"),
            "expected": expected,
            "replay_fixture": _relative_path(repo_root, replay_path),
        }
        records.append(
            EvalCaseRecord(
                case_id=input_path.stem,
                title=f"Email extraction {input_path.stem.removeprefix('email_')}",
                project_name="parentmate",
                agents="Email Extraction Agent",
                eval_type="Output Quality",
                description="Compares replay-backed structured extraction with the expected email fields.",
                expected_summary=_payload_json(expected),
                source_path=_relative_path(repo_root, input_path),
                payload_json=_payload_json(payload),
            )
        )
    return records


def _load_json_fixture_cases(repo_root: Path) -> list[EvalCaseRecord]:
    definitions = (
        ("career-guidance", "Career Advisor", "Expected skill gaps and development-plan completeness."),
        ("dream-translator", "Dream Analysis Agent", "Expected readiness, themes, insights, and prompt content."),
    )
    records: list[EvalCaseRecord] = []
    for project_name, agents, description in definitions:
        for path in sorted((repo_root / "projects" / project_name / "evals").glob("case_*.json")):
            payload = _load_json(path)
            expected = payload.get("expected", {}) if isinstance(payload, dict) else {}
            if project_name == "career-guidance" and isinstance(payload, dict):
                expected = {
                    key: value
                    for key, value in payload.items()
                    if key.startswith("expected_")
                }
            records.append(
                EvalCaseRecord(
                    case_id=path.stem,
                    title=f"{project_name.replace('-', ' ').title()} {path.stem.replace('_', ' ')}",
                    project_name=project_name,
                    agents=agents,
                    eval_type="Output Quality",
                    description=description,
                    expected_summary=_payload_json(expected),
                    source_path=_relative_path(repo_root, path),
                    payload_json=_payload_json(payload),
                )
            )
    return records


def _load_trip_planner_cases(repo_root: Path) -> list[EvalCaseRecord]:
    path = repo_root / "projects" / "Trip planner" / "tools" / "eval_runner.py"
    try:
        module = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    case_names: list[str] = []
    for node in module.body:
        value: ast.expr | None = None
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "CASES" for target in node.targets
        ):
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "CASES":
            value = node.value
        if isinstance(value, ast.List):
            for item in value.elts:
                if isinstance(item, ast.Tuple) and item.elts and isinstance(item.elts[0], ast.Constant):
                    case_names.append(str(item.elts[0].value))
    return [
        EvalCaseRecord(
            case_id=case_name,
            title=case_name.replace("_", " ").title(),
            project_name="Trip planner",
            agents="Trip Planning Agent",
            eval_type="Workflow",
            description="Executable planner behavior case defined in the project eval runner.",
            expected_summary="The named assertion function must complete without raising an error.",
            source_path=_relative_path(repo_root, path),
            payload_json=_payload_json({"case": case_name, "runner": _relative_path(repo_root, path)}),
        )
        for case_name in case_names
    ]


def _agents_for_eval_type(eval_type: str) -> str:
    if eval_type == "Output Quality":
        return "Learning Agent"
    if eval_type == "Workflow":
        return "PM, Experience Designer, Architect, Orchestrator, Learning Agent"
    if eval_type == "Memory":
        return "Learning Agent and memory-capable live roles"
    return "All bounded live agents"


def _normalized_items(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(value).strip() for value in values if str(value).strip()))


def evaluate_output_quality(
    output: str,
    *,
    required_terms: Iterable[str] = (),
    forbidden_terms: Iterable[str] = (),
    minimum_characters: int = 1,
) -> EvalResult:
    normalized = output.strip().lower()
    failures: list[str] = []
    if len(output.strip()) < minimum_characters:
        failures.append("output_too_short")
    for term in _normalized_items(required_terms):
        if term.lower() not in normalized:
            failures.append(f"missing_required_term:{term}")
    for term in _normalized_items(forbidden_terms):
        if term.lower() in normalized:
            failures.append(f"forbidden_term_present:{term}")
    return _result("Output Quality", failures, "output quality contract")


def evaluate_tool_selection(
    actual_tools: Iterable[str],
    *,
    expected_tools: Iterable[str],
    allowed_tools: Iterable[str],
    order_sensitive: bool = False,
) -> EvalResult:
    actual = _normalized_items(actual_tools)
    expected = _normalized_items(expected_tools)
    allowed = set(_normalized_items(allowed_tools))
    failures = [f"unauthorized_tool:{tool}" for tool in actual if tool not in allowed]
    failures.extend(f"missing_tool:{tool}" for tool in expected if tool not in actual)
    failures.extend(f"unnecessary_tool:{tool}" for tool in actual if tool not in expected)
    if order_sensitive and actual != expected:
        failures.append("incorrect_tool_order")
    return _result("Tool Selection", failures, "tool selection contract")


def evaluate_memory(
    output: str,
    *,
    required_facts: Iterable[str],
    forbidden_facts: Iterable[str] = (),
    memory_tool_required: bool = False,
    tools_used: Iterable[str] = (),
) -> EvalResult:
    normalized = output.lower()
    failures: list[str] = []
    for fact in _normalized_items(required_facts):
        if fact.lower() not in normalized:
            failures.append(f"missing_memory:{fact}")
    for fact in _normalized_items(forbidden_facts):
        if fact.lower() in normalized:
            failures.append(f"stale_memory_used:{fact}")
    if memory_tool_required and "read_project_memory" not in set(tools_used):
        failures.append("memory_tool_not_used")
    return _result("Memory", failures, "memory grounding contract")


def evaluate_cost(
    *,
    input_tokens: int,
    output_tokens: int,
    estimated_cost_usd: float | None,
    max_total_tokens: int,
    max_cost_usd: float,
) -> EvalResult:
    failures: list[str] = []
    total_tokens = max(0, input_tokens) + max(0, output_tokens)
    if total_tokens > max_total_tokens:
        failures.append("token_budget_exceeded")
    if estimated_cost_usd is None:
        failures.append("missing_cost_measurement")
    elif estimated_cost_usd > max_cost_usd:
        failures.append("cost_budget_exceeded")
    return _result("Cost", failures, "cost budget")


def evaluate_latency(*, duration_seconds: float | None, max_seconds: float) -> EvalResult:
    failures: list[str] = []
    if duration_seconds is None:
        failures.append("missing_latency_measurement")
    elif duration_seconds > max_seconds:
        failures.append("latency_budget_exceeded")
    return _result("Latency", failures, "latency budget")


def evaluate_reliability(
    outcomes: Iterable[bool],
    *,
    minimum_runs: int = 3,
    minimum_pass_rate: float = 0.95,
) -> EvalResult:
    values = tuple(bool(value) for value in outcomes)
    failures: list[str] = []
    if len(values) < minimum_runs:
        failures.append("insufficient_repeat_runs")
    pass_rate = sum(values) / len(values) if values else 0.0
    if pass_rate < minimum_pass_rate:
        failures.append("pass_rate_below_threshold")
    return _result("Reliability", failures, f"{sum(values)}/{len(values)} repeated runs passed")


def _result(eval_type: str, failures: list[str], contract: str) -> EvalResult:
    unique = tuple(dict.fromkeys(failures))
    score = max(0, round(100 * (1 - len(unique) / max(1, len(unique) + 1))))
    return EvalResult(
        eval_type=eval_type,
        passed=not unique,
        score=100 if not unique else score,
        summary=f"{contract}: {'passed' if not unique else f'{len(unique)} failure(s)'}",
        failures=unique,
    )
