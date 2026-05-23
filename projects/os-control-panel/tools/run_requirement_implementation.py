from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from workspace import (  # noqa: E402
    build_requirement_implementation_prompt,
    list_implementation_runs,
    update_implementation_run,
    _resolve_codex_executable,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a background Codex implementation flow for one requirement.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--requirement-id", required=True)
    return parser


def _read_output(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text().strip()


def main() -> int:
    args = build_parser().parse_args()
    run = next((item for item in list_implementation_runs() if item.run_id == args.run_id), None)
    if run is None:
        raise ValueError(f"Implementation run not found: {args.run_id}")

    started_at = datetime.now(timezone.utc).isoformat()
    update_implementation_run(args.run_id, status="RUNNING", started_at=started_at)

    output_path = Path(run.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    prompt = build_requirement_implementation_prompt(args.project_name, args.requirement_id)

    try:
        codex_executable = _resolve_codex_executable()
        result = subprocess.run(
            [
                str(codex_executable),
                "exec",
                "--full-auto",
                "--skip-git-repo-check",
                "--color",
                "never",
                "-C",
                str(REPO_ROOT),
                "-o",
                str(output_path),
                prompt,
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
    except Exception as exc:
        update_implementation_run(
            args.run_id,
            status="FAILED",
            error=str(exc),
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        return 1

    summary = _read_output(output_path)
    stderr = result.stderr.strip()
    stdout = result.stdout.strip()
    finished_at = datetime.now(timezone.utc).isoformat()

    if result.returncode != 0:
        error_parts = [part for part in [stderr, stdout] if part]
        update_implementation_run(
            args.run_id,
            status="FAILED",
            summary=summary,
            error="\n".join(error_parts) or f"Codex execution failed with exit code {result.returncode}.",
            finished_at=finished_at,
        )
        return result.returncode

    update_implementation_run(
        args.run_id,
        status="COMPLETED",
        summary=summary or "Implementation completed, but no final summary was captured.",
        error="",
        finished_at=finished_at,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
