from __future__ import annotations

import sys
from pathlib import Path
import unittest


SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from advisor import analyze_career_fit, format_gap_summary


CV_TEXT = """
Product analyst with experience in Excel reporting, customer interviews, and weekly commercial updates.
Led stakeholder workshops and presented recommendations to senior managers.
"""

TARGET_JOBS = """
Data Analyst role requiring Python, SQL, dashboard development in Power BI, machine learning fundamentals,
cloud deployment awareness, and stakeholder presentations.
"""


class CareerAdvisorTests(unittest.TestCase):
    def test_identifies_at_least_three_specific_gaps(self) -> None:
        result = analyze_career_fit(CV_TEXT, TARGET_JOBS)

        self.assertTrue(result["ready"])
        self.assertGreaterEqual(len(result["gaps"]), 3)
        gap_names = {gap["skill"] for gap in result["gaps"]}
        self.assertIn("Python data analysis", gap_names)
        self.assertIn("SQL and database querying", gap_names)
        self.assertIn("Dashboarding and business intelligence", gap_names)

    def test_development_plan_matches_gaps(self) -> None:
        result = analyze_career_fit(CV_TEXT, TARGET_JOBS)

        self.assertEqual(len(result["gaps"]), len(result["development_plan"]))
        for item in result["development_plan"]:
            self.assertTrue(item["focus_area"])
            self.assertTrue(item["next_step"])
            self.assertTrue(item["resource"])

    def test_does_not_invent_when_inputs_are_missing(self) -> None:
        result = analyze_career_fit("", TARGET_JOBS)

        self.assertFalse(result["ready"])
        self.assertEqual(result["gaps"], [])
        self.assertIn("required", result["warnings"][0])

    def test_summary_helper_is_concise(self) -> None:
        result = analyze_career_fit(CV_TEXT, TARGET_JOBS)

        self.assertEqual(
            format_gap_summary(result),
            f"{len(result['gaps'])} skill gaps identified with {len(result['development_plan'])} development actions.",
        )


if __name__ == "__main__":
    unittest.main()
