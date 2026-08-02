from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


SCHEMA_VERSION = "2026-07-22.pm-behavior-eval.v1"
DIMENSIONS = (
    "typed_output",
    "evidence_use",
    "tool_choice",
    "consultations",
    "approval_behavior",
    "guardrail_response",
    "trace_trajectory",
    "canonical_outcome",
)
SUPPORTED_MODES = {
    "discovery",
    "requirement_draft",
    "prioritisation",
    "task_plan",
    "artifact_review",
    "outcome_review",
}


@dataclass(frozen=True)
class PMBehaviorCase:
    case_id: str
    category: str
    title: str
    mode: str
    prompt: str
    rationale: str
    expectations: dict[str, Any]
    mock_trial: dict[str, Any]


@dataclass(frozen=True)
class PMDimensionGrade:
    dimension: str
    passed: bool
    score: int
    failures: tuple[str, ...]
    evidence: tuple[str, ...]


@dataclass(frozen=True)
class PMBehaviorGrade:
    case_id: str
    passed: bool
    score: int
    dimensions: tuple[PMDimensionGrade, ...]


@dataclass(frozen=True)
class PMEvalFingerprints:
    dataset: str
    prompt: str
    tool_policy: str
    guardrails: str
    model: str


def _stable_hash(value: object) -> str:
    serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(serialized.encode("utf-8")).hexdigest()


def load_pm_behavior_catalog(path: Path) -> tuple[str, tuple[PMBehaviorCase, ...]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to load PM behavior catalog: {exc}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"PM behavior catalog must use schema {SCHEMA_VERSION}")
    version = str(payload.get("dataset_version", "")).strip()
    raw_cases = payload.get("cases")
    defaults = payload.get("expectation_defaults", {})
    if not version or not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("PM behavior catalog requires dataset_version and cases")
    required = {"id", "category", "title", "mode", "prompt", "rationale", "expectations", "mock_trial"}
    cases: list[PMBehaviorCase] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_cases):
        if not isinstance(raw, dict):
            raise ValueError(f"PM behavior case {index} must be an object")
        missing = sorted(required - set(raw))
        if missing:
            raise ValueError(f"PM behavior case {index} missing fields: {', '.join(missing)}")
        case_id = str(raw["id"]).strip()
        if not case_id or case_id in seen:
            raise ValueError(f"PM behavior case IDs must be non-empty and unique: {case_id!r}")
        seen.add(case_id)
        mode = str(raw["mode"]).strip()
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"Unsupported PM mode for {case_id}: {mode}")
        expectations = _deep_merge(defaults, raw["expectations"])
        trial = raw["mock_trial"]
        if not isinstance(expectations, dict) or set(expectations) != set(DIMENSIONS):
            raise ValueError(f"{case_id} must define exactly the eight PM grading dimensions")
        if trial == "passing":
            trial = _passing_trial(expectations)
        if not isinstance(trial, dict):
            raise ValueError(f"{case_id} mock_trial must be an object or 'passing'")
        cases.append(
            PMBehaviorCase(
                case_id=case_id,
                category=str(raw["category"]).strip(),
                title=str(raw["title"]).strip(),
                mode=mode,
                prompt=str(raw["prompt"]).strip(),
                rationale=str(raw["rationale"]).strip(),
                expectations=expectations,
                mock_trial=trial,
            )
        )
    return version, tuple(cases)


def _deep_merge(base: object, override: object) -> dict[str, Any]:
    if not isinstance(base, dict) or not isinstance(override, dict):
        return dict(override) if isinstance(override, dict) else {}
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _passing_trial(expectations: dict[str, Any]) -> dict[str, Any]:
    typed = expectations["typed_output"]
    evidence = expectations["evidence_use"]
    tools = expectations["tool_choice"]
    consultations = expectations["consultations"]
    approval = expectations["approval_behavior"]
    guardrails = expectations["guardrail_response"]
    trace = expectations["trace_trajectory"]
    canonical = expectations["canonical_outcome"]
    return {
        "typed_output": {
            "mode": typed.get("mode"),
            "status": typed.get("status"),
            "next_action": typed.get("next_action"),
            "fields": {field: "present" for field in typed.get("required_fields", [])},
        },
        "evidence_use": {
            "references": [f"synthetic-evidence-{index + 1}" for index in range(int(evidence.get("minimum_references", 0)))],
            "claims": [],
        },
        "tool_choice": {"tools": list(tools.get("required", []))},
        "consultations": {"roles": list(consultations.get("required_roles", []))},
        "approval_behavior": {"action": approval.get("action", "")},
        "guardrail_response": {"codes": list(guardrails.get("required_codes", []))},
        "trace_trajectory": {"events": list(trace.get("required_events", []))},
        "canonical_outcome": {"outcome": canonical.get("outcome", "")},
    }


def _ordered_subset(expected: Iterable[str], actual: Iterable[str]) -> bool:
    iterator = iter(actual)
    return all(any(candidate == item for candidate in iterator) for item in expected)


def _grade_dimension(dimension: str, expected: dict[str, Any], trial: dict[str, Any]) -> PMDimensionGrade:
    failures: list[str] = []
    evidence: list[str] = []
    actual = trial.get(dimension, {})
    if not isinstance(actual, dict):
        actual = {}
        failures.append("missing_dimension_record")

    if dimension == "typed_output":
        for field in ("mode", "status", "next_action"):
            wanted = expected.get(field)
            allowed_values = expected.get("allowed_values", {}).get(field, [])
            if allowed_values:
                if actual.get(field) not in allowed_values:
                    failures.append(f"unexpected_{field}")
            elif wanted is not None and actual.get(field) != wanted:
                failures.append(f"unexpected_{field}")
        for field in expected.get("required_fields", []):
            if not actual.get("fields", {}).get(field):
                failures.append(f"missing_field:{field}")
    elif dimension == "evidence_use":
        references = [str(item) for item in actual.get("references", [])]
        if len(references) < int(expected.get("minimum_references", 0)):
            failures.append("insufficient_evidence")
        claims = " ".join(str(item) for item in actual.get("claims", [])).lower()
        for phrase in expected.get("forbidden_claims", []):
            if str(phrase).lower() in claims:
                failures.append(f"unsupported_claim:{phrase}")
        evidence.extend(references)
    elif dimension == "tool_choice":
        tools = [str(item) for item in actual.get("tools", [])]
        required = [str(item) for item in expected.get("required", [])]
        allowed = {str(item) for item in expected.get("allowed", [])}
        aliases = {
            str(tool): {str(alias) for alias in values}
            for tool, values in expected.get("semantic_aliases", {}).items()
            if isinstance(values, list)
        }
        failures.extend(
            f"missing_tool:{tool}"
            for tool in required
            if not ({tool} | aliases.get(tool, set())).intersection(tools)
        )
        failures.extend(f"unauthorized_tool:{tool}" for tool in tools if tool not in allowed)
        normalized_tools = [
            next(
                (
                    semantic
                    for semantic, equivalents in aliases.items()
                    if tool in equivalents
                ),
                tool,
            )
            for tool in tools
        ]
        if expected.get("ordered") and not _ordered_subset(required, normalized_tools):
            failures.append("incorrect_tool_order")
        evidence.extend(tools)
    elif dimension == "consultations":
        roles = [str(item) for item in actual.get("roles", [])]
        failures.extend(
            f"missing_consultation:{role}"
            for role in expected.get("required_roles", [])
            if role not in roles
        )
        failures.extend(
            f"unnecessary_consultation:{role}"
            for role in roles
            if role not in expected.get("allowed_roles", [])
        )
        evidence.extend(roles)
    elif dimension == "approval_behavior":
        wanted = str(expected.get("action", ""))
        observed = str(actual.get("action", ""))
        if observed != wanted:
            failures.append(f"approval_action:{observed or 'missing'}!={wanted}")
        evidence.append(observed)
    elif dimension == "guardrail_response":
        codes = [str(item) for item in actual.get("codes", [])]
        failures.extend(f"missing_guardrail:{code}" for code in expected.get("required_codes", []) if code not in codes)
        failures.extend(f"forbidden_guardrail:{code}" for code in expected.get("forbidden_codes", []) if code in codes)
        evidence.extend(codes)
    elif dimension == "trace_trajectory":
        events = [str(item) for item in actual.get("events", [])]
        wanted = [str(item) for item in expected.get("required_events", [])]
        if not _ordered_subset(wanted, events):
            failures.append("incorrect_trace_trajectory")
        terminal = str(expected.get("terminal_event", ""))
        if terminal and (not events or events[-1] != terminal):
            failures.append(f"incorrect_terminal_event:{events[-1] if events else 'missing'}")
        evidence.extend(events)
    elif dimension == "canonical_outcome":
        wanted = str(expected.get("outcome", ""))
        observed = str(actual.get("outcome", ""))
        if observed != wanted:
            failures.append(f"canonical_outcome:{observed or 'missing'}!={wanted}")
        evidence.append(observed)

    unique = tuple(dict.fromkeys(failures))
    return PMDimensionGrade(
        dimension=dimension,
        passed=not unique,
        score=100 if not unique else max(0, 100 - 20 * len(unique)),
        failures=unique,
        evidence=tuple(item for item in evidence if item),
    )


def grade_pm_behavior(case: PMBehaviorCase, trial: dict[str, Any]) -> PMBehaviorGrade:
    dimensions = tuple(
        _grade_dimension(name, case.expectations[name], trial)
        for name in DIMENSIONS
    )
    return PMBehaviorGrade(
        case_id=case.case_id,
        passed=all(item.passed for item in dimensions),
        score=round(mean(item.score for item in dimensions)),
        dimensions=dimensions,
    )


def build_fingerprints(
    *,
    dataset_payload: object,
    prompt_payload: object,
    tool_policy_payload: object,
    guardrail_payload: object,
    model_label: str,
) -> PMEvalFingerprints:
    return PMEvalFingerprints(
        dataset=_stable_hash(dataset_payload),
        prompt=_stable_hash(prompt_payload),
        tool_policy=_stable_hash(tool_policy_payload),
        guardrails=_stable_hash(guardrail_payload),
        model=_stable_hash({"model_label": model_label}),
    )


def aggregate_pm_trials(
    *,
    dataset_version: str,
    backend: str,
    model_label: str,
    fingerprints: PMEvalFingerprints,
    grades: Iterable[PMBehaviorGrade],
    minimum_trials: int = 3,
    minimum_pass_rate: float = 0.95,
) -> dict[str, Any]:
    grouped: dict[str, list[PMBehaviorGrade]] = {}
    for grade in grades:
        grouped.setdefault(grade.case_id, []).append(grade)
    cases: dict[str, Any] = {}
    all_grades = [grade for values in grouped.values() for grade in values]
    for case_id in sorted(grouped):
        values = grouped[case_id]
        pass_rate = sum(item.passed for item in values) / len(values)
        failure_counts: dict[str, int] = {}
        for grade in values:
            for dimension in grade.dimensions:
                for failure in dimension.failures:
                    key = f"{dimension.dimension}:{failure}"
                    failure_counts[key] = failure_counts.get(key, 0) + 1
        dimension_scores = {
            dimension: round(mean(
                next(item.score for item in grade.dimensions if item.dimension == dimension)
                for grade in values
            ), 2)
            for dimension in DIMENSIONS
        }
        cases[case_id] = {
            "trials": len(values),
            "pass_rate": round(pass_rate, 4),
            "mean_score": round(mean(item.score for item in values), 2),
            "minimum_score": min(item.score for item in values),
            "maximum_score": max(item.score for item in values),
            "dimension_scores": dimension_scores,
            "failure_counts": dict(sorted(failure_counts.items())),
            "threshold_passed": len(values) >= minimum_trials and pass_rate >= minimum_pass_rate,
        }
    overall_pass_rate = sum(item.passed for item in all_grades) / len(all_grades) if all_grades else 0.0
    return {
        "schema_version": SCHEMA_VERSION,
        "dataset_version": dataset_version,
        "generated_at": datetime.now(UTC).isoformat(),
        "backend": backend,
        "billing_boundary": billing_boundary(backend),
        "model_label": model_label,
        "fingerprints": asdict(fingerprints),
        "thresholds": {"minimum_trials": minimum_trials, "minimum_pass_rate": minimum_pass_rate},
        "overall": {
            "cases": len(cases),
            "trials": len(all_grades),
            "pass_rate": round(overall_pass_rate, 4),
            "mean_score": round(mean(item.score for item in all_grades), 2) if all_grades else 0.0,
            "threshold_passed": bool(cases) and all(item["threshold_passed"] for item in cases.values()),
        },
        "cases": cases,
        "limitations": [
            "Deterministic mock success validates the evaluation contract, not live PM reasoning quality.",
            "Pass-rate observations describe only the recorded trial count and are not statistical confidence claims.",
            "Live backend comparisons are meaningful only when their revision fingerprints and dataset version are recorded.",
        ],
    }


def compare_pm_reports(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    regressions: list[str] = []
    improvements: list[str] = []
    baseline_cases = baseline.get("cases", {})
    candidate_cases = candidate.get("cases", {})
    for case_id in sorted(set(baseline_cases) | set(candidate_cases)):
        if case_id not in candidate_cases:
            regressions.append(f"missing_case:{case_id}")
            continue
        if case_id not in baseline_cases:
            improvements.append(f"new_case:{case_id}")
            continue
        old = float(baseline_cases[case_id].get("mean_score", 0))
        new = float(candidate_cases[case_id].get("mean_score", 0))
        if new < old:
            regressions.append(f"case_score:{case_id}:{old}->{new}")
        elif new > old:
            improvements.append(f"case_score:{case_id}:{old}->{new}")
        for dimension in DIMENSIONS:
            old_dimension = float(baseline_cases[case_id].get("dimension_scores", {}).get(dimension, 0))
            new_dimension = float(candidate_cases[case_id].get("dimension_scores", {}).get(dimension, 0))
            if new_dimension < old_dimension:
                regressions.append(f"dimension:{case_id}:{dimension}:{old_dimension}->{new_dimension}")
    return {
        "comparable": baseline.get("dataset_version") == candidate.get("dataset_version"),
        "fingerprint_changes": sorted(
            key
            for key in set(baseline.get("fingerprints", {})) | set(candidate.get("fingerprints", {}))
            if baseline.get("fingerprints", {}).get(key) != candidate.get("fingerprints", {}).get(key)
        ),
        "regressions": regressions,
        "improvements": improvements,
        "passed": not regressions,
    }


def billing_boundary(backend: str) -> str:
    boundaries = {
        "deterministic": "No model tokens; local deterministic execution.",
        "codex": "Consumes Codex plan or credits; exact token counts may be unavailable.",
        "agents-sdk": "Consumes OpenAI API project tokens and model requests.",
    }
    if backend not in boundaries:
        raise ValueError(f"Unsupported PM evaluation backend: {backend}")
    return boundaries[backend]


def require_live_authorization(*, backend: str, live: bool, billing_acknowledged: bool) -> None:
    billing_boundary(backend)
    if backend == "deterministic":
        return
    if not live or not billing_acknowledged:
        raise PermissionError(
            f"{backend} PM evaluations are live model-backed trials. Pass both explicit live and billing acknowledgement gates. "
            f"{billing_boundary(backend)}"
        )
