from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"


def evaluate_project_traces(project_name: str) -> dict[str, object]:
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))

    from agents_runtime.support import grade_agent_traces, load_agent_traces

    return grade_agent_traces(load_agent_traces(project_name))


def main() -> int:
    parser = argparse.ArgumentParser(description="Grade captured AI Builder OS live-agent traces.")
    parser.add_argument("--project", default="os-control-panel")
    args = parser.parse_args()

    result = evaluate_project_traces(args.project)
    status = "PASS" if result["passed"] else "FAIL"
    print(f"{status} live_agent_trace_quality - {result['summary']}")
    for failure in result["failures"]:
        print(f"  {failure}")
    passed = 1 if result["passed"] else 0
    print(f"SUMMARY: {passed}/1 passing")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
