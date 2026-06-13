from __future__ import annotations

import difflib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"
REPLAY_DIR = EVALS_DIR / "replays"

sys.path.insert(0, str(REPO_ROOT))

from projects.parentmate.src.extractor import extract_email_from_response_content  # noqa: E402
from tools.common import find_orphan_product_artifacts


IGNORED_COMPARISON_FIELDS = {"confidence", "title"}


def comparable_output(value: Any) -> Any:
    """Return a copy with non-deterministic fields removed for eval comparison."""
    if isinstance(value, dict):
        return {
            key: comparable_output(item)
            for key, item in value.items()
            if key not in IGNORED_COMPARISON_FIELDS
        }

    if isinstance(value, list):
        return [comparable_output(item) for item in value]

    return value


def parse_eval_input(path: Path) -> tuple[str, str]:
    raw = path.read_text().strip()
    lines = raw.splitlines()

    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
        return subject, body

    return "", raw


def format_json(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True)


def replay_path_for(input_path: Path) -> Path:
    return REPLAY_DIR / f"{input_path.stem}_response.json"


def main() -> int:
    orphan_artifacts = find_orphan_product_artifacts(PROJECT_ROOT)
    if orphan_artifacts:
        for orphan in orphan_artifacts:
            print(f"FAIL orphan product artifact — {orphan}")
        return 1
    print("PASS product artifact audit — no orphan product artifacts")

    eval_files = sorted(EVALS_DIR.glob("email_*.txt"))
    failures = 0

    if not eval_files:
        print(f"No eval input files found in {EVALS_DIR}")
        return 1

    if not REPLAY_DIR.exists():
        print(f"No replay fixtures found in {REPLAY_DIR}")
        return 1

    for input_path in eval_files:
        expected_path = input_path.with_name(f"{input_path.stem}_expected.json")
        replay_path = replay_path_for(input_path)
        if not expected_path.exists():
            failures += 1
            print(f"CASE {input_path.stem}: FAIL")
            print(f"Missing expected JSON: {expected_path}")
            print("---")
            continue
        if not replay_path.exists():
            failures += 1
            print(f"CASE {input_path.stem}: FAIL")
            print(f"Missing replay response JSON: {replay_path}")
            print("---")
            continue

        subject, body = parse_eval_input(input_path)

        replay_content = replay_path.read_text()
        actual = extract_email_from_response_content(subject, body, replay_content).model_dump(
            mode="json"
        )
        expected = json.loads(expected_path.read_text())

        comparable_actual = comparable_output(deepcopy(actual))
        comparable_expected = comparable_output(deepcopy(expected))
        passed = comparable_actual == comparable_expected

        if not passed:
            failures += 1

        print(f"CASE {input_path.stem}: {'PASS' if passed else 'FAIL'}")
        print(f"SUBJECT: {subject or '<empty>'}")
        print("ACTUAL:")
        print(format_json(actual))

        if not passed:
            print("EXPECTED:")
            print(format_json(expected))
            print("DIFF:")
            diff = difflib.unified_diff(
                format_json(comparable_expected).splitlines(),
                format_json(comparable_actual).splitlines(),
                fromfile="expected_comparable",
                tofile="actual_comparable",
                lineterm="",
            )
            print("\n".join(diff))

        print("---")

    total = len(eval_files)
    print(f"SUMMARY: {total - failures}/{total} passing")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
