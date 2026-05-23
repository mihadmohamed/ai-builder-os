from __future__ import annotations

import sys
import unittest
from pathlib import Path

from scenario_eval_runner import run_scenarios

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests" / "unit"
REPO_ROOT = PROJECT_ROOT.parents[1]


def main() -> int:
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    unit_total = 0
    unit_passed = 0
    unit_success = True

    if not TESTS_DIR.exists():
        print("No unit test directory found.")
        unit_success = False
    else:
        suite = unittest.defaultTestLoader.discover(str(TESTS_DIR), pattern="test_*.py")
        unit_total = suite.countTestCases()
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        unit_passed = unit_total - len(result.failures) - len(result.errors)
        unit_success = result.wasSuccessful()

    scenario_results = run_scenarios()
    scenario_total = len(scenario_results)
    scenario_passed = sum(1 for item in scenario_results if item.passed)
    for item in scenario_results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status} {item.fixture.scenario_id} — {item.fixture.title}")
        print(f"  {item.detail}")

    total = unit_total + scenario_total
    passed = unit_passed + scenario_passed
    print(f"SUMMARY: {passed}/{total} passing")
    return 0 if unit_success and scenario_passed == scenario_total else 1


if __name__ == "__main__":
    raise SystemExit(main())
