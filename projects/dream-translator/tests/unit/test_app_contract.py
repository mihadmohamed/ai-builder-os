from __future__ import annotations

from pathlib import Path
import unittest


APP_SOURCE = Path(__file__).resolve().parents[2] / "src" / "app.py"


class AppContractTests(unittest.TestCase):
    def test_ui_keeps_primary_flow_visible(self) -> None:
        source = APP_SOURCE.read_text(encoding="utf-8")

        self.assertIn("Dream description", source)
        self.assertIn("Visual style", source)
        self.assertIn("Translate dream", source)
        self.assertIn("st.session_state", source)
        self.assertIn("Image prompt", source)


if __name__ == "__main__":
    unittest.main()
