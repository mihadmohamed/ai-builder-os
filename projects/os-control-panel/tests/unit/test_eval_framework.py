from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "src"
TOOLS_ROOT = REPO_ROOT / "projects" / "os-control-panel" / "tools"
for path in (SRC_ROOT, TOOLS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import eval_framework  # noqa: E402
from capability_eval_runner import run_capability_evals  # noqa: E402


class EvalFrameworkTests(unittest.TestCase):
    def test_capability_suite_covers_and_passes_all_eight_eval_types(self) -> None:
        results = run_capability_evals()

        self.assertEqual({item.result.eval_type for item in results}, set(eval_framework.EVAL_TYPE_DESCRIPTIONS))
        self.assertTrue(all(item.result.passed for item in results))

    def test_tool_selection_detects_missing_unnecessary_and_order_failures(self) -> None:
        result = eval_framework.evaluate_tool_selection(
            ["read_tasks", "read_project_memory"],
            expected_tools=["read_requirements", "read_tasks"],
            allowed_tools=["read_requirements", "read_tasks", "read_project_memory"],
            order_sensitive=True,
        )

        self.assertFalse(result.passed)
        self.assertIn("missing_tool:read_requirements", result.failures)
        self.assertIn("unnecessary_tool:read_project_memory", result.failures)
        self.assertIn("incorrect_tool_order", result.failures)

    def test_memory_detects_missing_stale_and_unretrieved_context(self) -> None:
        result = eval_framework.evaluate_memory(
            "Use the retired manual route.",
            required_facts=["deterministic routing"],
            forbidden_facts=["retired manual route"],
            memory_tool_required=True,
            tools_used=[],
        )

        self.assertFalse(result.passed)
        self.assertEqual(len(result.failures), 3)

    def test_cost_latency_and_reliability_fail_their_thresholds(self) -> None:
        cost = eval_framework.evaluate_cost(
            input_tokens=9000,
            output_tokens=5000,
            estimated_cost_usd=0.08,
            max_total_tokens=12000,
            max_cost_usd=0.05,
        )
        latency = eval_framework.evaluate_latency(duration_seconds=12.0, max_seconds=10.0)
        reliability = eval_framework.evaluate_reliability(
            [True, False],
            minimum_runs=3,
            minimum_pass_rate=0.95,
        )

        self.assertFalse(cost.passed)
        self.assertFalse(latency.passed)
        self.assertFalse(reliability.passed)

    def test_coverage_catalog_maps_every_eval_type_to_agents_and_projects(self) -> None:
        covered = {item.eval_type for item in eval_framework.EVAL_COVERAGE}

        self.assertEqual(covered, set(eval_framework.EVAL_TYPE_DESCRIPTIONS))
        self.assertTrue(all(item.project_name and item.agents and item.implementation for item in eval_framework.EVAL_COVERAGE))

    def test_case_catalog_normalizes_cases_from_every_evaluated_project(self) -> None:
        cases = eval_framework.load_eval_case_catalog(REPO_ROOT)
        projects = {item.project_name for item in cases}

        self.assertEqual(
            projects,
            {"os-control-panel", "parentmate", "career-guidance", "dream-translator", "Trip planner"},
        )
        self.assertGreaterEqual(len(cases), 57)
        self.assertEqual(
            {item.eval_type for item in cases},
            set(eval_framework.EVAL_TYPE_DESCRIPTIONS),
        )
        self.assertTrue(all(item.source_path and item.payload_json for item in cases))

    def test_trip_planner_code_defined_cases_are_visible_in_catalog(self) -> None:
        cases = eval_framework.load_eval_case_catalog(REPO_ROOT)
        trip_case_ids = {
            item.case_id for item in cases if item.project_name == "Trip planner"
        }

        self.assertIn("budget_locality_and_weather", trip_case_ids)
        self.assertIn("activity_selection_payloads", trip_case_ids)


if __name__ == "__main__":
    unittest.main()
