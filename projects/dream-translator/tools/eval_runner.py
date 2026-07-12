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

from dream_analyzer import analyze_dream
from tools.common import find_orphan_product_artifacts


def main() -> int:
    orphan_artifacts = find_orphan_product_artifacts(PROJECT_ROOT)
    if orphan_artifacts:
        for orphan in orphan_artifacts:
            print(f"FAIL orphan product artifact — {orphan}")
        return 1
    print("PASS product artifact audit — no orphan product artifacts")

    eval_files = sorted(EVALS_DIR.glob("*.json"))
    if not eval_files:
        print("No eval input files found.")
        print("SUMMARY: 0/0 passing")
        return 1

    passed = 0
    for eval_file in eval_files:
        case = json.loads(eval_file.read_text(encoding="utf-8"))
        result = analyze_dream(case["dream_text"], case.get("style", "Watercolor"))
        expected = case["expected"]
        failures: list[str] = []

        if result["ready"] != expected["ready"]:
            failures.append(f"ready expected {expected['ready']} got {result['ready']}")
        if len(result.get("insights", [])) < expected["minimum_insights"]:
            failures.append("not enough insights")
        if expected["theme_contains"] not in result.get("theme", ""):
            failures.append("theme mismatch")

        prompt = result.get("visual", {}).get("image_prompt", "")
        for required_text in expected.get("prompt_contains", []):
            if required_text not in prompt:
                failures.append(f"prompt missing {required_text!r}")

        if failures:
            print(f"FAIL {eval_file.name}: {'; '.join(failures)}")
        else:
            passed += 1
            print(f"PASS {eval_file.name}")

    print(f"SUMMARY: {passed}/{len(eval_files)} passing")
    return 0 if passed == len(eval_files) else 1


if __name__ == "__main__":
    raise SystemExit(main())
