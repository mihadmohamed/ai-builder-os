from __future__ import annotations

from pathlib import Path
import unittest


APP_SOURCE = Path(__file__).resolve().parents[2] / "src" / "app.py"


class AppGuidanceTests(unittest.TestCase):
    def test_target_job_input_explains_multiple_postings(self) -> None:
        source = APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("Paste one job posting or several postings into this same field", source)
        self.assertIn("Separate each posting", source)
        self.assertIn("Posting 1:", source)
        self.assertIn("Posting 2:", source)
        self.assertIn("---", source)


if __name__ == "__main__":
    unittest.main()
