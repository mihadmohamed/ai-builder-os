from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from common import PROJECTS_ROOT, REPO_ROOT
SUMMARY_PATTERN = re.compile(r"^SUMMARY:\s+(\d+)/(\d+)\s+passing$")
FAIL_PATTERN = re.compile(r"^CASE\s+(\S+):\s+FAIL$")


def resolve_runner(project_name: str, mode: str) -> Path | None:
    if mode == "live":
        live_runner = PROJECTS_ROOT / project_name / "tools" / "live_eval_runner.py"
        if live_runner.exists():
            return live_runner

    project_runner = PROJECTS_ROOT / project_name / "tools" / "eval_runner.py"
    if project_runner.exists():
        return project_runner


    return None


def run_runner(runner_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(runner_path)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def parse_report(output: str) -> tuple[tuple[int, int] | None, list[str]]:
    summary: tuple[int, int] | None = None
    failures: list[str] = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        summary_match = SUMMARY_PATTERN.match(line)
        if summary_match:
            summary = (int(summary_match.group(1)), int(summary_match.group(2)))
            continue

        fail_match = FAIL_PATTERN.match(line)
        if fail_match:
            failures.append(fail_match.group(1))

    return summary, failures


def reliability_statement(summary: tuple[int, int] | None, return_code: int) -> str:
    if return_code != 0 and summary is None:
        return "Low confidence: the validation path did not complete cleanly."

    if summary is None:
        return "Low confidence: no summary was produced by the validation runner."

    passed, total = summary
    if total == 0:
        return "Low confidence: no eval cases were reported."

    if passed == total:
        return "High confidence: the current validation suite is passing."

    if passed / total >= 0.8:
        return "Medium confidence: most evals are passing, but regressions are present."

    return "Low confidence: the validation suite shows substantial instability."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run a project eval runner and format the results as a QA report."
    )
    parser.add_argument("project_name", help="Project name under projects/")
    parser.add_argument(
        "--mode",
        choices=("deterministic", "live"),
        default="deterministic",
        help="Validation mode. Defaults to deterministic replay-backed validation.",
    )
    parser.add_argument(
        "--show-runner-output",
        action="store_true",
        help="Include the raw runner output after the QA summary.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    runner_path = resolve_runner(args.project_name, args.mode)
    if runner_path is None:
        print("Summary: FAIL")
        print("Key failures:")
        print(f"- No {args.mode} validation runner could be found for this project.")
        print("Possible causes:")
        if args.mode == "live":
            print("- Project-local live eval tooling is missing.")
        else:
            print("- Project-local deterministic eval tooling is missing.")
        print("Confidence in system reliability: Low confidence: no validation path is available.")
        return 1

    completed = run_runner(runner_path)
    combined_output = completed.stdout.strip()
    if completed.stderr.strip():
        combined_output = f"{combined_output}\n{completed.stderr.strip()}".strip()

    summary, failures = parse_report(combined_output)

    print("Summary:")
    if summary is None:
        print("- FAIL: no parseable pass/fail summary was found")
    else:
        passed, total = summary
        status = "PASS" if completed.returncode == 0 else "FAIL"
        print(f"- {status}: {passed}/{total} passing ({args.mode})")

    print("Key failures:")
    if failures:
        for case in failures[:10]:
            print(f"- {case}")
    elif completed.returncode != 0:
        print("- Validation failed, but no individual failing case markers were parsed.")
    else:
        print("- None")

    print("Possible causes:")
    if completed.returncode != 0 and summary is None:
        print("- The validation runner failed before producing structured results.")
    elif failures:
        print("- One or more eval outputs diverged from expected results.")
    else:
        print("- No clear failure signal in the current eval run.")

    print(f"Confidence in system reliability: {reliability_statement(summary, completed.returncode)}")

    if args.show_runner_output:
        print()
        print("Raw runner output:")
        print(combined_output or "<no output>")

    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
