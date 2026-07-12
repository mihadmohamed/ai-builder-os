from __future__ import annotations

import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"
SRC_DIR = PROJECT_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from advisor import analyze_career_fit
from tools.common import find_orphan_product_artifacts


def main() -> int:
    orphan_artifacts = find_orphan_product_artifacts(PROJECT_ROOT)
    if orphan_artifacts:
        for orphan in orphan_artifacts:
            print(f"FAIL orphan product artifact — {orphan}")
        return 1
    print("PASS product artifact audit — no orphan product artifacts")

    eval_files = sorted(EVALS_DIR.glob("case_*.json"))
    if not eval_files:
        print("No eval case files found.")
        print("SUMMARY: 0/0 passing")
        return 1

    passed = 0
    failures: list[str] = []

    for eval_file in eval_files:
        case = json.loads(eval_file.read_text())
        result = analyze_career_fit(case["cv_text"], case["target_jobs"])
        gap_names = {gap["skill"] for gap in result["gaps"]}
        expected_gaps = set(case.get("expected_gaps", []))
        min_gaps = int(case.get("expected_min_gaps", 0))

        case_failures: list[str] = []
        if not result["ready"]:
            case_failures.append("analysis was not ready")
        if len(result["gaps"]) < min_gaps:
            case_failures.append(f"expected at least {min_gaps} gaps, found {len(result['gaps'])}")
        missing = sorted(expected_gaps - gap_names)
        if missing:
            case_failures.append(f"missing expected gaps: {', '.join(missing)}")
        if len(result["development_plan"]) != len(result["gaps"]):
            case_failures.append("development plan count did not match gap count")

        if case_failures:
            failures.append(f"{eval_file.name}: {'; '.join(case_failures)}")
            print(f"FAIL {eval_file.name}")
        else:
            passed += 1
            print(f"PASS {eval_file.name}")

    total = len(eval_files)
    print(f"SUMMARY: {passed}/{total} passing")
    if failures:
        for failure in failures:
            print(failure)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
