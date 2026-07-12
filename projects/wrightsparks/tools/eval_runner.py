from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = PROJECT_ROOT / "evals"


def main() -> int:
    eval_files = sorted(EVALS_DIR.glob("*.txt"))
    if not eval_files:
        print("No eval input files found.")
        print("SUMMARY: 0/0 passing")
        print("Project-specific deterministic validation has not been implemented yet.")
        return 1

    print("This template eval runner is a starter stub.")
    print("Replace it with project-specific deterministic validation logic.")
    print(f"Found {len(eval_files)} eval input file(s) in {EVALS_DIR}.")
    print("SUMMARY: 0/0 passing")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
