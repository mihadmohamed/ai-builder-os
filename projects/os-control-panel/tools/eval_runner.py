from __future__ import annotations

import sys
import unittest
from pathlib import Path

from scenario_eval_runner import run_scenarios
from capability_eval_runner import run_capability_evals
from codex_native_eval_runner import run_codex_native_evals
from sdk_contract_eval_runner import run_sdk_contract_evals

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TESTS_DIR = PROJECT_ROOT / "tests" / "unit"
REPO_ROOT = PROJECT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.common import audit_learning_agent_wrapper, find_orphan_product_artifacts


def main() -> int:
    unit_total = 0
    unit_passed = 0
    unit_success = True
    artifact_success = True
    wrapper_success = True

    orphan_artifacts = find_orphan_product_artifacts(PROJECT_ROOT)
    if orphan_artifacts:
        artifact_success = False
        for orphan in orphan_artifacts:
            print(f"FAIL orphan product artifact — {orphan}")
    else:
        print("PASS product artifact audit — no orphan product artifacts")

    wrapper_issues = audit_learning_agent_wrapper()
    if wrapper_issues:
        wrapper_success = False
        for issue in wrapper_issues:
            print(f"FAIL learning-agent wrapper audit — {issue}")
    else:
        print("PASS learning-agent wrapper audit — hosted wrapper stays aligned to canonical learning behavior")

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

    capability_results = run_capability_evals()
    capability_total = len(capability_results)
    capability_passed = sum(1 for item in capability_results if item.result.passed)
    for item in capability_results:
        status = "PASS" if item.result.passed else "FAIL"
        print(f"{status} {item.case_id} — {item.result.eval_type}")
        print(f"  {item.result.summary}")

    sdk_results = run_sdk_contract_evals()
    sdk_total = len(sdk_results)
    sdk_passed = sum(1 for item in sdk_results if item.passed)
    for item in sdk_results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status} {item.case_id} — OpenAI Agents SDK contract")
        print(f"  {item.detail}")

    codex_results = run_codex_native_evals()
    codex_total = len(codex_results)
    codex_passed = sum(1 for item in codex_results if item.passed)
    for item in codex_results:
        status = "PASS" if item.passed else "FAIL"
        print(f"{status} {item.case_id} — Codex-native contract")
        print(f"  {item.detail}")

    total = unit_total + scenario_total + capability_total + sdk_total + codex_total
    passed = unit_passed + scenario_passed + capability_passed + sdk_passed + codex_passed
    print(f"SUMMARY: {passed}/{total} passing")
    return 0 if (
        artifact_success
        and wrapper_success
        and unit_success
        and scenario_passed == scenario_total
        and capability_passed == capability_total
        and sdk_passed == sdk_total
        and codex_passed == codex_total
    ) else 1


if __name__ == "__main__":
    raise SystemExit(main())
