from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
CASES_FILE = PROJECT_ROOT / "evals" / "eval_cases.json"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from agent_runtime import grade_agent_traces  # noqa: E402
from eval_framework import (  # noqa: E402
    EvalResult,
    evaluate_cost,
    evaluate_latency,
    evaluate_memory,
    evaluate_output_quality,
    evaluate_reliability,
    evaluate_tool_selection,
)


@dataclass(frozen=True)
class CapabilityEvalResult:
    case_id: str
    result: EvalResult


def run_capability_evals() -> list[CapabilityEvalResult]:
    cases = json.loads(CASES_FILE.read_text(encoding="utf-8"))
    results: list[CapabilityEvalResult] = []
    for case in cases:
        eval_type = case["eval_type"]
        if eval_type == "Output Quality":
            result = evaluate_output_quality(
                case["output"],
                required_terms=case.get("required_terms", []),
                forbidden_terms=case.get("forbidden_terms", []),
                minimum_characters=20,
            )
        elif eval_type == "Tool Selection":
            result = evaluate_tool_selection(
                case["actual_tools"],
                expected_tools=case["expected_tools"],
                allowed_tools=case["allowed_tools"],
                order_sensitive=case.get("order_sensitive", False),
            )
        elif eval_type == "Memory":
            result = evaluate_memory(
                case["output"],
                required_facts=case["required_facts"],
                forbidden_facts=case.get("forbidden_facts", []),
                memory_tool_required=case.get("memory_tool_required", False),
                tools_used=case.get("tools_used", []),
            )
        elif eval_type == "Cost":
            result = evaluate_cost(
                input_tokens=case["input_tokens"],
                output_tokens=case["output_tokens"],
                estimated_cost_usd=case["estimated_cost_usd"],
                max_total_tokens=case["max_total_tokens"],
                max_cost_usd=case["max_cost_usd"],
            )
        elif eval_type == "Latency":
            result = evaluate_latency(
                duration_seconds=case["duration_seconds"],
                max_seconds=case["max_seconds"],
            )
        elif eval_type == "Reliability":
            result = evaluate_reliability(
                case["outcomes"],
                minimum_runs=case["minimum_runs"],
                minimum_pass_rate=case["minimum_pass_rate"],
            )
        else:
            trace_grade = grade_agent_traces(case["trace"])
            result = EvalResult(
                eval_type=eval_type,
                passed=bool(trace_grade["passed"]),
                score=int(trace_grade["score"]),
                summary=str(trace_grade["summary"]),
                failures=tuple(str(item) for item in trace_grade["failures"]),
            )
        results.append(CapabilityEvalResult(case_id=case["id"], result=result))
    return results


if __name__ == "__main__":
    evaluated = run_capability_evals()
    for item in evaluated:
        print(f"{'PASS' if item.result.passed else 'FAIL'} {item.case_id} - {item.result.summary}")
    passed = sum(1 for item in evaluated if item.result.passed)
    print(f"SUMMARY: {passed}/{len(evaluated)} passing")
    raise SystemExit(0 if passed == len(evaluated) else 1)
