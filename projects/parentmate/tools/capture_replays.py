from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"
REPLAY_DIR = EVALS_DIR / "replays"

sys.path.insert(0, str(REPO_ROOT))

from projects.parentmate.src.extractor import request_extraction_response_content  # noqa: E402


def parse_eval_input(path: Path) -> tuple[str, str]:
    raw = path.read_text().strip()
    lines = raw.splitlines()

    if lines and lines[0].lower().startswith("subject:"):
        subject = lines[0].split(":", 1)[1].strip()
        body = "\n".join(lines[1:]).strip()
        return subject, body

    return "", raw


def replay_path_for(input_path: Path) -> Path:
    return REPLAY_DIR / f"{input_path.stem}_response.json"


def main() -> int:
    requested_stems = set(sys.argv[1:])
    eval_files = sorted(EVALS_DIR.glob("email_*.txt"))
    if requested_stems:
        eval_files = [path for path in eval_files if path.stem in requested_stems]

    if not eval_files:
        print(f"No eval input files found in {EVALS_DIR}")
        return 1

    REPLAY_DIR.mkdir(parents=True, exist_ok=True)

    for input_path in eval_files:
        subject, body = parse_eval_input(input_path)
        replay_path = replay_path_for(input_path)
        response_content = request_extraction_response_content(subject, body)
        replay_path.write_text(response_content + "\n")
        print(f"CAPTURED: {replay_path.relative_to(PROJECT_ROOT)}")

    print(f"SUMMARY: captured {len(eval_files)} replay responses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
