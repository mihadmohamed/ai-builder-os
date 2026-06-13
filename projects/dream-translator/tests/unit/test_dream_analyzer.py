from __future__ import annotations

import sys
from pathlib import Path
import unittest


SRC_DIR = Path(__file__).resolve().parents[2] / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dream_analyzer import analyze_dream, format_insight_count


DREAM_TEXT = """
I was walking through my childhood house during a flood.
A bright door opened into the sky and I felt scared but curious.
"""


class DreamAnalyzerTests(unittest.TestCase):
    def test_interpretation_contains_at_least_three_distinct_insights(self) -> None:
        result = analyze_dream(DREAM_TEXT, "Surreal")

        self.assertTrue(result["ready"])
        self.assertGreaterEqual(len(result["insights"]), 3)
        labels = {item["label"] for item in result["insights"]}
        self.assertIn("Emotional state", labels)
        self.assertIn("Symbolic pattern", labels)
        self.assertIn("Personal aspiration", labels)

    def test_visual_representation_is_theme_and_style_aware(self) -> None:
        result = analyze_dream(DREAM_TEXT, "Surreal")

        visual = result["visual"]
        self.assertEqual(visual["style"], "Surreal")
        self.assertIn("Surreal", visual["image_prompt"])
        self.assertIn("symbolic", visual["image_prompt"])
        self.assertIn("<svg", visual["svg"])
        self.assertIn("dreamscape", visual["svg"])

    def test_short_input_does_not_invent_interpretation(self) -> None:
        result = analyze_dream("A door.", "Watercolor")

        self.assertFalse(result["ready"])
        self.assertEqual(result["insights"], [])
        self.assertIn("required", result["warnings"][0])

    def test_summary_helper_reports_insight_count(self) -> None:
        result = analyze_dream(DREAM_TEXT, "Surreal")

        self.assertEqual(format_insight_count(result), f"{len(result['insights'])} insights generated")


if __name__ == "__main__":
    unittest.main()
