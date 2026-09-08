"""Privacy-safe, observation-only evaluation contracts for R120 executors."""
from __future__ import annotations

from dataclasses import dataclass


EVALUATION_VERSION = "r120-executor-evals-v1"
_CATEGORIES = ("deterministic", "structured", "classification", "tools", "discovery", "review", "edit", "implementation", "debugging", "architecture")


@dataclass(frozen=True)
class ExecutorEvaluationCase:
    case_id: str
    category: str
    eligible_tiers: tuple[str, ...]
    requires_tools: bool = False


@dataclass(frozen=True)
class ExecutorEvaluationObservation:
    case_id: str
    tier: str
    status: str  # passed, failed, unavailable
    validation_passed: bool | None = None
    latency_ms: int | None = None
    allowance_telemetry: str = "unavailable"


def default_cases() -> tuple[ExecutorEvaluationCase, ...]:
    """Thirty fixed, non-prompt cases; no raw work content is retained."""
    return tuple(
        ExecutorEvaluationCase(f"r120-{category}-{number}", category, ("deterministic", "local", "luna", "terra", "sol"), category == "tools")
        for category in _CATEGORIES for number in range(1, 4)
    )


def report(observations: tuple[ExecutorEvaluationObservation, ...], cases: tuple[ExecutorEvaluationCase, ...] | None = None) -> dict[str, object]:
    cases = cases or default_cases()
    valid_ids = {case.case_id for case in cases}
    if any(item.case_id not in valid_ids for item in observations):
        raise ValueError("Unknown executor evaluation case")
    unavailable = sum(item.status == "unavailable" for item in observations)
    complete = len({item.case_id for item in observations}) == len(cases)
    passed = sum(item.status == "passed" and item.validation_passed is True for item in observations)
    # Observation evidence never promotes local routing by itself.
    return {"version": EVALUATION_VERSION, "case_count": len(cases), "observed_count": len(observations), "validated_pass_count": passed, "unavailable_count": unavailable, "coverage_complete": complete, "promotion_eligible": False, "promotion_blocker": "OBSERVATION_MODE_REQUIRES_CONTROLLER_POLICY_AND_REQUEST_TYPE_EVIDENCE"}
