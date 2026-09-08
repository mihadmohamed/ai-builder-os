from __future__ import annotations

import unittest

from executor_evaluation import ExecutorEvaluationObservation, default_cases, report


class ExecutorEvaluationTests(unittest.TestCase):
    def test_catalog_has_thirty_cases_across_every_required_category(self):
        cases = default_cases()
        self.assertEqual(len(cases), 30)
        self.assertEqual({case.category for case in cases}, {"deterministic", "structured", "classification", "tools", "discovery", "review", "edit", "implementation", "debugging", "architecture"})

    def test_unavailable_is_explicit_and_never_promotes_local_routing(self):
        cases = default_cases()
        result = report(tuple(ExecutorEvaluationObservation(case.case_id, "local", "unavailable") for case in cases))
        self.assertTrue(result["coverage_complete"])
        self.assertEqual(result["unavailable_count"], 30)
        self.assertFalse(result["promotion_eligible"])

    def test_unknown_case_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            report((ExecutorEvaluationObservation("unknown", "local", "passed", True),))
