from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOT = REPO_ROOT / "projects" / "os-control-panel"
for path in (PROJECT_ROOT / "src", PROJECT_ROOT / "tools"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from eval_framework import load_eval_case_catalog  # noqa: E402
from pm_behavioral_eval_runner import run_pm_behavioral_evals  # noqa: E402
from pm_behavioral_evals import (  # noqa: E402
    DIMENSIONS,
    PMBehaviorGrade,
    aggregate_pm_trials,
    build_fingerprints,
    compare_pm_reports,
    grade_pm_behavior,
    load_pm_behavior_catalog,
    require_live_authorization,
)


CASES_FILE = PROJECT_ROOT / "evals" / "pm_behavioral_cases.json"


class PMBehavioralEvalTests(unittest.TestCase):
    def test_catalog_is_versioned_representative_and_shared(self) -> None:
        version, cases = load_pm_behavior_catalog(CASES_FILE)
        categories = {case.category for case in cases}

        self.assertEqual(version, "pm-baseline-2026-07-22.v1")
        self.assertGreaterEqual(len(cases), 15)
        self.assertTrue({
            "vague_discovery", "complete_brief", "conflicting_stakeholders",
            "ownership_concurrency", "duplicates", "uncertain_effort", "validation_first",
            "specialist_selection", "acceptance_quality", "ai_agent_requirements",
            "prompt_injection", "unauthorized_mutation", "artifact_review", "outcome_review",
        }.issubset(categories))
        shared = load_eval_case_catalog(REPO_ROOT)
        shared_ids = {item.case_id for item in shared}
        self.assertTrue({case.case_id for case in cases}.issubset(shared_ids))

    def test_catalog_rejects_duplicates_and_incomplete_contracts(self) -> None:
        payload = json.loads(CASES_FILE.read_text(encoding="utf-8"))
        payload["cases"][1]["id"] = payload["cases"][0]["id"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unique"):
                load_pm_behavior_catalog(path)

        payload = json.loads(CASES_FILE.read_text(encoding="utf-8"))
        del payload["expectation_defaults"]["canonical_outcome"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cases.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "eight PM grading dimensions"):
                load_pm_behavior_catalog(path)

    def test_grader_reports_actionable_failures_in_every_dimension(self) -> None:
        _, cases = load_pm_behavior_catalog(CASES_FILE)
        case = next(item for item in cases if item.case_id == "pm-complete-brief-ready")
        bad = deepcopy(case.mock_trial)
        bad["typed_output"] = {}
        bad["evidence_use"] = {"references": [], "claims": ["already implemented and deployed"]}
        bad["tool_choice"] = {"tools": ["mutate_requirements"]}
        bad["consultations"] = {"roles": ["Unknown"]}
        bad["approval_behavior"] = {"action": "self_approve"}
        bad["guardrail_response"] = {"codes": ["unauthorized_mutation_accepted"]}
        bad["trace_trajectory"] = {"events": ["run_started", "run_completed", "tool_called"]}
        bad["canonical_outcome"] = {"outcome": "changed_without_approval"}

        result = grade_pm_behavior(case, bad)

        self.assertFalse(result.passed)
        self.assertEqual({item.dimension for item in result.dimensions}, set(DIMENSIONS))
        self.assertTrue(all(not item.passed and item.failures for item in result.dimensions))

    def test_deterministic_runner_creates_three_trial_baseline_without_api(self) -> None:
        report = run_pm_behavioral_evals()

        self.assertEqual(report["backend"], "deterministic")
        self.assertEqual(report["overall"]["cases"], 16)
        self.assertEqual(report["overall"]["trials"], 48)
        self.assertTrue(report["overall"]["threshold_passed"])
        self.assertTrue(report["generated_at"].endswith("+00:00"))
        self.assertIn("No model tokens", report["billing_boundary"])
        self.assertEqual(set(report["fingerprints"]), {"dataset", "prompt", "tool_policy", "guardrails", "model"})

    def test_repeated_trials_expose_variance_and_comparison_regressions(self) -> None:
        version, cases = load_pm_behavior_catalog(CASES_FILE)
        case = cases[0]
        passing = grade_pm_behavior(case, case.mock_trial)
        bad_trial = deepcopy(case.mock_trial)
        bad_trial["canonical_outcome"] = {"outcome": "wrong"}
        failing = grade_pm_behavior(case, bad_trial)
        fingerprints = build_fingerprints(
            dataset_payload={"v": 1}, prompt_payload={"v": 1}, tool_policy_payload={"v": 1},
            guardrail_payload={"v": 1}, model_label="mock",
        )
        baseline = aggregate_pm_trials(
            dataset_version=version, backend="deterministic", model_label="mock",
            fingerprints=fingerprints, grades=[passing, passing, passing],
        )
        candidate = aggregate_pm_trials(
            dataset_version=version, backend="deterministic", model_label="mock",
            fingerprints=fingerprints, grades=[passing, failing, passing],
        )

        self.assertEqual(candidate["cases"][case.case_id]["minimum_score"], failing.score)
        self.assertEqual(candidate["cases"][case.case_id]["maximum_score"], passing.score)
        self.assertIn(
            "canonical_outcome:canonical_outcome:wrong!=unchanged",
            candidate["cases"][case.case_id]["failure_counts"],
        )
        comparison = compare_pm_reports(baseline, candidate)
        self.assertFalse(comparison["passed"])
        self.assertTrue(any(item.startswith("case_score:") for item in comparison["regressions"]))
        self.assertTrue(any(":canonical_outcome:" in item for item in comparison["regressions"]))

    def test_live_backends_fail_closed_and_accept_host_trial_contract(self) -> None:
        for backend in ("codex", "agents-sdk"):
            with self.assertRaises(PermissionError):
                require_live_authorization(backend=backend, live=False, billing_acknowledged=False)
            with self.assertRaises(ValueError):
                run_pm_behavioral_evals(
                    backend=backend,
                    live=True,
                    billing_acknowledged=True,
                    trial_records=None,
                )

        _, cases = load_pm_behavior_catalog(CASES_FILE)
        case = cases[0]
        records = [{"case_id": case.case_id, "trial": case.mock_trial} for _ in range(3)]
        report = run_pm_behavioral_evals(
            backend="codex",
            model_label="host-captured-test",
            live=True,
            billing_acknowledged=True,
            trial_records=records,
        )
        self.assertTrue(report["overall"]["threshold_passed"])
        self.assertIn("Codex plan or credits", report["billing_boundary"])


if __name__ == "__main__":
    unittest.main()
